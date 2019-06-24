import os
import pickle

import requests


COOKIES_FILENAME = 'cian_cookies.bin'


class CianReqSession(object):
    _instance = None

    @staticmethod
    def instance():
        if CianReqSession._instance is None:
            CianReqSession._instance = requests.session()
            CianReqSession.load_cookies()
        return CianReqSession._instance

    @staticmethod
    def load_cookies():
        if CianReqSession._instance is None:
            return
        if os.path.isfile(COOKIES_FILENAME):
            with open(COOKIES_FILENAME, 'rb') as file:
                CianReqSession._instance.cookies.update(pickle.load(file))

    @staticmethod
    def save_cookies():
        if CianReqSession._instance is None:
            return
        with open(COOKIES_FILENAME, 'wb') as file:
            pickle.dump(CianReqSession._instance.cookies, file)