import json
import urllib.parse as urlparse
from collections import defaultdict

from cian import captcha
from cian.session import CianReqSession
from cian.utils import clusterize_w_limit, ConvexHull, Point
from settings import CIAN_MAX_RESULT_SIZE

BASIC_INFO_URL = 'https://www.cian.ru/cian-api/mobile-site/v2/offers/clusters/'
DETAILED_INFO_URL = 'https://www.cian.ru/cian-api/mobile-site/v1/map-search-offers/'

HEADERS = {
    'Pragma': 'no-cache',
    'Origin': 'https://www.cian.ru',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Cache-Control': 'no-cache',
    'Referer': 'https://www.cian.ru/map/?deal_type=rent&engine_version=2&in_polygon%5B1%5D=37.4951_55.8224%2C37.4956_55.8209%2C37.4966_55.8195%2C37.4977_55.8181%2C37.4996_55.8171%2C37.5022_55.8169%2C37.5048_55.8171%2C37.5075_55.8174%2C37.5101_55.8178%2C37.5125_55.8184%2C37.5149_55.8191%2C37.5175_55.8195%2C37.5199_55.8201%2C37.5221_55.8209%2C37.5244_55.8216%2C37.5268_55.8221%2C37.5284_55.8233%2C37.5304_55.8244%2C37.5322_55.8255%2C37.5328_55.8276%2C37.5327_55.8291%2C37.5322_55.8306%2C37.532_55.8321%2C37.5338_55.8333%2C37.5357_55.8343%2C37.538_55.8353%2C37.54_55.8363%2C37.542_55.8373%2C37.5428_55.8387%2C37.5412_55.8399%2C37.5387_55.8401%2C37.5361_55.8399%2C37.5338_55.8392%2C37.5316_55.8384%2C37.529_55.8387%2C37.5274_55.8376%2C37.5255_55.8366%2C37.5245_55.8352%2C37.5228_55.8341%2C37.5216_55.8327%2C37.5201_55.8315%2C37.5184_55.8304%2C37.5175_55.829%2C37.5169_55.8276%2C37.5152_55.8264%2C37.5128_55.8256%2C37.5103_55.825%2C37.5078_55.8246%2C37.5051_55.8243%2C37.5022_55.8238%2C37.4997_55.8234%2C37.4972_55.8229%2C37.4949_55.8222&offer_type=flat&polygon_name%5B1%5D=%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C+%D0%BF%D0%BE%D0%B8%D1%81%D0%BA%D0%B0&room2=1&type=4&zoom=13&center=55.82542101735545,37.54156982031251&pin_opened=TRUE',
    'Connection': 'keep-alive',
}

USABLE_FIELDS = {
    # о сдающем
    "phones": None,
    "user": {
        "phoneNumbers": None,
        "userTrustLevel": None,
        "agencyName": None,
        "companyName": None,
        "agencyNameV2": None,
        "cianUserId": None,
        "isChatsEnabled": None,
        "experience": None,
        "isSubAgent": True,
        "userType": None,
        "agentAccountType": None,
        "isAgent": None,
        "isHidden": None,
        "cianProfileStatus": None,
    },
    "publishedUserId": None,

    # общие детали
    "userId": None,
    "floorNumber": None,
    "repairType": None,
    "roomType": None,
    "allRoomsArea": None,
    "totalArea": None,
    "kitchenArea": None,
    "flatType": None,
    "title": None,
    "description": None,
    "windowsViewType": None,
    "isNew": None,
    "livingArea": None,
    "roomsCount": None,
    "bedsCount": None,
    "demolishedInMoscowProgramm": None,
    "building": {
        "cargoLiftsCount": None,
        "materialType": None,
        "series": None,
        "buildYear": None,
        "hasGarbageChute": None,
        "totalArea": None,
        "houseMaterialType": None,
        "passengerLiftsCount": None,
        "floorsCount": None,
        "ceilingHeight": None,
    },
    "photos": None,

    # удобства
    "hasFurniture": None,
    "hasConditioner": None,
    "balconiesCount": None,
    "loggiasCount": None,
    "separateWcsCount": None,
    "combinedWcsCount": None,
    "hasDishwasher": None,
    "hasFridge": None,
    "hasInternet": None,
    "hasPhone": None,
    "hasShower": None,
    "hasTv": None,
    "hasWasher": None,
    "hasKitchenFurniture": None,
    "hasBathtub": None,

    # дети животные
    "childrenAllowed": None,
    "petsAllowed": None,

    # об объявлении
    "id": None,
    "cianId": None,
    "cianUserId": None,
    "isFairplay": None,
    "isByHomeowner": None,
    "withoutClientFee": None,
    "added": None,
    "editDate": None,
    "statistic": {
        "total": None,
        "daily": None
    },
    "priceChanges": None,
    "isDuplicatedDescription": None,
    "isRentByParts": None,
    "isPaid": None,
    "isPro": None,
    "category": None,
    "isColorized": None,
    "isHiddenByUser": None,
    "isTop3": None,
    "publishTerms": {
        "autoprolong": None,
    },
    "isAuction": None,
    "status": None,
    "isPremium": None,
    "dealType": None,
    "isInHiddenBase": None,
    "bargainTerms": {
        "paymentPeriod": None,
        "price": None,
        "currency": "rur",
        "deposit": 53000,
        "clientFee": 50,
        "bargainAllowed": False,
        "prepayMonths": 1,
        "leaseTermType": "longTerm",
        "agentFee": 50,
        "priceType": "all",
    },
}


BROWSER_URL = 'https://www.cian.ru/map/?currency=2&deal_type=rent&engine_version=2&in_polygon%5B1%5D=37.4689_55.857%2C37.4716_55.8628%2C37.4806_55.8657%2C37.4909_55.8665%2C37.5001_55.8636%2C37.5077_55.8595%2C37.5152_55.8551%2C37.5201_55.8498%2C37.5228_55.8442%2C37.529_55.8394%2C37.5372_55.8355%2C37.5396_55.8296%2C37.54_55.8238%2C37.5424_55.818%2C37.5427_55.812%2C37.5472_55.8066%2C37.5499_55.8009%2C37.5475_55.795%2C37.5437_55.7895%2C37.5355_55.7859%2C37.5249_55.7851%2C37.5146_55.7859%2C37.5077_55.7922%2C37.5115_55.7977%2C37.507_55.8031%2C37.4977_55.8058%2C37.4922_55.811%2C37.4888_55.817%2C37.4871_55.8228%2C37.4843_55.8284%2C37.4809_55.834%2C37.4765_55.8394%2C37.4727_55.8448%2C37.4689_55.857&maxprice=55000&offer_type=flat&polygon_name%5B1%5D=%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C+%D0%BF%D0%BE%D0%B8%D1%81%D0%BA%D0%B0&room2=1&type=4&zoom=12&center=55.84707394035329,37.50939999999998'
# FIXME: берется из запроса в BASIC_INFO, можно рассчитать, найдя координаты, полностью охватывающие полигон
BBOX = '55.779701895594826,37.3492399353027,55.935532886597926,37.66956006469723'


class CianConnector(object):
    @staticmethod
    def generate_polygon_string(polygon_points):
        result = []
        for x, y in polygon_points:
            result.append(f'{x}_{y}')
        return ','.join(result)

    @staticmethod
    def get_query_string(polygon_points=None):
        parsed = urlparse.urlparse(BROWSER_URL)
        qs = urlparse.parse_qsl(parsed.query)
        simple_query = urlparse.urlencode(qs)
        if polygon_points:
            new_qs = []
            for field_name, value in qs:
                if 'in_polygon' in field_name:
                    new_value = CianConnector.generate_polygon_string(polygon_points)
                    new_qs.append((field_name, new_value))
                else:
                    new_qs.append((field_name, value))
            qs = new_qs
        query = urlparse.urlencode(qs)
        return query

    @staticmethod
    def get_basic_offers():
        query_string = CianConnector.get_query_string()
        url = f'{BASIC_INFO_URL}/?{query_string}&screen_area=301&bbox={BBOX}'
        resp = CianReqSession.instance().get(url, headers=HEADERS)
        raw_data = resp.content.decode('utf-8')

        if 'captcha' in raw_data:
            print('Captcha needed!')
            captcha.solve_recaptcha(resp.url, raw_data)
            return CianConnector.get_basic_offers()
        raw_data = json.loads(raw_data)
        raw_data = raw_data['data']
        offers = raw_data['offers']
        return offers

    @staticmethod
    def clusterize_basic_offers(offers):
        offer_map = {}
        coords_list = []
        for offer in offers:
            lon, lat = offer['lon'], offer['lat']
            offer_map[(lon, lat)] = offer
            coords_list.append([lon, lat])
        cluster_map = clusterize_w_limit(coords_list, CIAN_MAX_RESULT_SIZE)
        result = defaultdict(list)
        for cluster_id, coordinates_list in cluster_map.items():
            coordinates_list = tuple(tuple(c) for c in coordinates_list)
            for coords in coordinates_list:
                result[cluster_id].append(offer_map[coords])
        return result

    @staticmethod
    def get_convex_hulls(clusterized_offers):
        hulls = {}
        for cluster_id, offers in clusterized_offers.items():
            convex_hull = ConvexHull()
            for offer in offers:
                lat, lon = offer['lat'], offer['lon']
                convex_hull.add(Point(lon, lat))
            hull_points = convex_hull.get_hull_points()
            hulls[cluster_id] = [(h.x, h.y) for h in hull_points]
        return hulls


    @staticmethod
    def extract_info(full_info, usable_fields=None):
        extracted_info = {}
        if not full_info:
            return {}
        if not usable_fields:
            usable_fields = USABLE_FIELDS
        for key, value in usable_fields.items():
            if key not in full_info:
                continue
            if value is None:
                extracted_info[key] = full_info[key]
            elif type(value) is dict:
                extracted_info[key] = CianConnector.extract_info(full_info[key], value)
        return extracted_info

    @staticmethod
    def get_offers(polygon_points):
        query_string = CianConnector.get_query_string(polygon_points)
        data = {
            "_subdomain": "www",
            "_path": f'/?{query_string}'
        }
        resp = CianReqSession.instance().post(DETAILED_INFO_URL, data=json.dumps(data).encode('utf-8'), headers=HEADERS)
        raw_data = resp.content.decode('utf-8')

        if 'captcha' in raw_data:
            print('Captcha needed!')
            captcha.solve_recaptcha(resp.url, raw_data)
            return CianConnector.get_offers(polygon_points)
        raw_data = json.loads(raw_data)
        raw_data = raw_data['data']
        offers = raw_data['offersSerialized']
        result = []
        for offer in offers:
            extracted = CianConnector.extract_info(offer)
            result.append(extracted)
        return result
