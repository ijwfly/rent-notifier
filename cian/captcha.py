import json
import re
import time
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

import settings
from cian.session import CianReqSession


RUCAPCHA_URL = 'https://rucaptcha.com/in.php'
RUCAPCHA_GET_URL = 'https://rucaptcha.com/res.php'


def extract_captcha_b64(html):
    soup = BeautifulSoup(html, features='html.parser')
    tag = soup.find('img')
    return tag.attrs['src']


def send_to_solve(b64image):
    data = {
        'method': 'base64',
        'key': settings.RUCAPCHA_TOKEN,
        'body': b64image,
        'json': 1,
    }
    resp = requests.instance().post(RUCAPCHA_URL, data=data)
    print(resp.content)


def exract_recaptcha(html):
    key = None
    soup = BeautifulSoup(html, features='html.parser')
    tag = soup.find('script')
    result = re.search("'sitekey': '(.+?)'", tag.text)
    if result:
        key = result.group(1)
    return key


def send_to_solve_recapcha(url, google_key):
    data = {
        'method': 'userrecaptcha',
        'key': settings.RUCAPCHA_TOKEN,
        'pageurl': url,
        'googlekey': google_key,
        'json': 1,
    }
    resp = requests.post(RUCAPCHA_URL, data=data)
    print(resp.content)
    return json.loads(resp.content.decode('utf-8'))


def check_status(request_id):
    data = {
        'key': settings.RUCAPCHA_TOKEN,
        'action': 'get',
        'id': int(request_id),
        'json': 1,
    }
    resp = requests.get(RUCAPCHA_GET_URL, params=data)
    print(resp.content)
    status = json.loads(resp.content.decode('utf-8'))
    return status


def send_recaptcha_answer(url, captcha_key):
    data = {
        'g-recaptcha-response': captcha_key,
        'redirect_url': parse_qs(urlparse(url).query)['redirect_url'],
    }
    print(data)
    resp = CianReqSession.instance().post(url, data=data)
    print(resp.content)
    CianReqSession.save_cookies()
    print(CianReqSession.instance().cookies)


def solve_recaptcha(url, raw_html):
    key = exract_recaptcha(raw_html)
    print('Sending captcha to solve...')
    print(f'url: {url}')
    resp = send_to_solve_recapcha(url, key)
    request_id = resp['request']
    print(f'Captcha sent, request_id: {request_id}. Waiting 20 seconds...')
    time.sleep(20)
    while True:
        status = check_status(request_id)
        if status['request'] == 'CAPCHA_NOT_READY':
            print('Captcha still not ready, waiting...')
            time.sleep(5)
        else:
            captcha_key = status['request']
            break
    send_recaptcha_answer(url, captcha_key)
