from pymongo import MongoClient

import settings


class MongoOffers:
    _instance = None

    def __init__(self):
        self.collection = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)[settings.MONGO_CIAN_COLLECTION]

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = MongoOffers()
        return cls._instance

    def upsert_offer(self, offer):
        return self.collection.offers.update_one({'cianId': offer['cianId']}, {'$set': offer}, upsert=True)

    def get_offer(self, cian_id):
        return self.collection.offers.find_one({'cianId': cian_id})
