import locale
import time
import traceback

import settings
from cian.cianapi import CianConnector
from mongo_collection import MongoOffers
from dictdiffer import diff

from telegram_notifier import CianNotifierBot


class CianProcessor:
    offers = MongoOffers.instance()

    @staticmethod
    def compare_offers(db_offer, offer):
        if db_offer.get('_id') is not None:
            del db_offer['_id']
        diff_result = diff(db_offer, offer)
        return diff_result

    def process_current_offer(self, offer):
        cian_id = offer['cianId']
        db_offer = self.offers.get_offer(cian_id)
        if db_offer:
            diff_result = self.compare_offers(db_offer, offer)
            if diff_result:
                CianNotifierBot.send_offer_changed(offer, diff_result)
        else:
            CianNotifierBot.send_new_offer(offer)
        return self.offers.upsert_offer(offer)

    def process(self):
        print('Starting cian processor...')
        while True:
            try:
                print('Reading offers...')
                offers = CianConnector.get_offers()
                print(f'Got {len(offers)} offers...')
                for offer in offers:
                    self.process_current_offer(offer)

                interval = settings.CIAN_UPDATE_INTERVAL
                print(f'Sleeping {interval} seconds...')
                time.sleep(interval)
            except Exception as e:
                print(f'Exception occured: {e}')
                print(f'Traceback: {traceback.format_exc()}')
                interval = settings.CIAN_UPDATE_INTERVAL_ERROR
                print(f'Sleeping {interval} seconds...')
                time.sleep(interval)


if __name__ == '__main__':
    # initialize locale to show currencies correctly
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

    processor = CianProcessor()
    processor.process()
