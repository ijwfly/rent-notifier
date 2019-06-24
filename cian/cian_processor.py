import time

from pymongo import MongoClient

import settings
from cian.cianapi import CianConnector


def update_offers(collection):
    print('Reading offers...')
    offers = CianConnector.get_offers()
    print(f'Got {len(offers)} offers...')
    for offer in offers:
        result = collection.offers.update_one({'cianId': offer['cianId']}, {'$set': offer}, upsert=True)
        print(result)
        input('waiting...')


def process():
    print('Starting cian processor...')
    print('Connecting to mongo...')
    mongo = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    collection = mongo['cian_offers']
    while True:
        update_offers(collection)
        # print(collection.offers.find_one({}))
        time.sleep(settings.CIAN_UPDATE_INTERVAL)


if __name__ == '__main__':
    process()
