#coding=utf- 8
import requests
from enum import Enum
import time
from bs4 import BeautifulSoup
import trafilatura
import os

subscription_key = os.environ.get('BING_SEARCH_KEY', '')
endpoint = "https://api.bing.microsoft.com/v7.0/search"
mkt = 'en-US'
headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

class CONTENT_TYPE(Enum):
    SEARCH_RESULT = 0
    RESULT_TARGET_PAGE = 1

class ContentItem:
    def __init__(self, type: CONTENT_TYPE, data):
        self.type = type
        self.data = data

class Operator():
    def __init__(self):
        self.content = []

    def search(self, key_words, filter=None) -> list:
        start_time = time.time()
        try:
            result = requests.get(endpoint, headers=headers, params={'q': key_words, 'mkt': mkt }, timeout=10)
        except Exception:
            result = requests.get(endpoint, headers=headers, params={'q': key_words, 'mkt': mkt }, timeout=10)
        if result.status_code == 200:
            result = result.json()

            self.content = []
            self.content.append(ContentItem(CONTENT_TYPE.SEARCH_RESULT, result))
        else:
            result = requests.get(endpoint, headers=headers, params={'q': key_words, 'mkt': mkt }, timeout=10)
            if result.status_code == 200:
                result = result.json()

                self.content = []
                self.content.append(ContentItem(CONTENT_TYPE.SEARCH_RESULT, result))
            else:
                raise Exception('Platform search error. Do you register your Bing API key?')
        print(f'search time:{time.time() - start_time}s')
        return self.content[-1].data["webPages"]["value"]

    def get_page_num(self) -> int:
        return len(self.content[-1].data)

    def load_page(self, idx:int) -> str:
        try:
            top = self.content[-1].data["webPages"]["value"]
            res = requests.get(top[idx]['url'], timeout=10)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            content = res.text
            soup = BeautifulSoup(content, 'html.parser')
            text = trafilatura.extract(soup.prettify())
                
            return top[idx]['url'], text
        except:
            return None, None