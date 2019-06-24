import json
from cian import captcha
from cian.session import CianReqSession

BASE_URL = 'https://www.cian.ru/cian-api/mobile-site/v1/map-search-offers/'

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

DATA = {
    "_subdomain": "www",
    "_path":"/?deal_type=1&engine_version=2&in_polygon%5B1%5D=37.4951_55.8224,37.4956_55.8209,37.4966_55.8195,37.4977_55.8181,37.4996_55.8171,37.5022_55.8169,37.5048_55.8171,37.5075_55.8174,37.5101_55.8178,37.5125_55.8184,37.5149_55.8191,"
            "37.5175_55.8195,37.5199_55.8201,37.5221_55.8209,37.5244_55.8216,37.5268_55.8221,37.5284_55.8233,37.5304_55.8244,37.5322_55.8255,37.5328_55.8276,37.5327_55.8291,37.5322_55.8306,37.532_55.8321,37.5338_55.8333,37.5357_55.8343,37."
            "538_55.8353,37.54_55.8363,37.542_55.8373,37.5428_55.8387,37.5412_55.8399,37.5387_55.8401,37.5361_55.8399,37.5338_55.8392,37.5316_55.8384,37.529_55.8387,37.5274_55.8376,37.5255_55.8366,37.5245_55.8352,37.5228_55.8341,37.5216_55."
            "8327,37.5201_55.8315,37.5184_55.8304,37.5175_55.829,37.5169_55.8276,37.5152_55.8264,37.5128_55.8256,37.5103_55.825,37.5078_55.8246,37.5051_55.8243,37.5022_55.8238,37.4997_55.8234,37.4972_55.8229,37.4949_55.8222&offer_type=flat&"
            "polygon_name%5B1%5D=Область+поиска&room2=1&type=4"
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


class CianConnector(object):

    @staticmethod
    def extract_info(full_info, usable_fields=None):
        extracted_info = {}
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
    def get_offers():
        resp = CianReqSession.instance().post(BASE_URL, data=json.dumps(DATA).encode('utf-8'), headers=HEADERS)
        raw_data = resp.content.decode('utf-8')

        if 'captcha' in raw_data:
            print('Captcha needed!')
            captcha.solve_recaptcha(resp.url, raw_data)
            return CianConnector.get_offers()
        raw_data = json.loads(raw_data)
        raw_data = raw_data['data']
        offers = raw_data['offersSerialized']
        result = []
        for offer in offers:
            extracted = CianConnector.extract_info(offer)
            result.append(extracted)
        return result
