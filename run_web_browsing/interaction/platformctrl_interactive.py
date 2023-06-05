#coding=utf- 8
import copy
import math
import requests
from enum import Enum
import time
from bs4 import BeautifulSoup
import trafilatura
import os
from tenacity import retry, stop_after_attempt, wait_fixed

subscription_key = os.environ.get('BING_SEARCH_KEY', '')
endpoint = "https://api.bing.microsoft.com/v7.0/search"
mkt = 'en-US'
headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

#  search result list chunk size
SEARCH_RESULT_LIST_CHUNK_SIZE = 3
#  result target page text chunk content length
RESULT_TARGET_PAGE_PER_TEXT_COUNT = 500

class Operation(Enum):
    PAGE_DOWN = 'A'
    PAGE_UP = 'B'
    GO_BACK = 'C'
    ADD_DIGEST = 'D'
    MERGE = 'E'
    LOAD_PAGE_1 = 'F'
    LOAD_PAGE_2 = 'G'
    LOAD_PAGE_3 = 'H'
    END = 'I'
    SEARCH = 'J'
    START = 'K'
    REJECT = 'L'
    TO_TOP = 'M'

class CONTENT_TYPE(Enum):
    SEARCH_RESULT = 0
    RESULT_TARGET_PAGE = 1

class ContentItem:
    def __init__(self, type: CONTENT_TYPE, data):
        self.type = type
        self.data = data

class DigestData:
    title: str
    desc: str
    chunkIndex: int

class Digest:
    datas: list
    checked: bool

class Operator():
    def __init__(self):
        self.topic = None
        self.content = []
        self.digests = []
        self.curResultChunk = 0
        self.curTargetPageResultChunk = 0

    def _isSearchResultPage(self):
        return self.content[-1].type == CONTENT_TYPE.SEARCH_RESULT

    def _isResultContentPage(self):
        return self.content[-1].type == CONTENT_TYPE.RESULT_TARGET_PAGE


    def execute(self, operation, *args, **kwargs):
        """Execute operation.

        Keyword arguments:

        operation -- operation to be executed

        extra_info -- extra information for the operation
            start->[optional]topic\n
            search->key words, filter\n
            load_page->index of the search result\n
            add_digest->content\n
            merge->index of digests, use list
        """
        if operation == Operation.START:
            self.start(*args, **kwargs)
        elif operation == Operation.SEARCH:
            self.search(*args, **kwargs)
        elif operation == Operation.LOAD_PAGE_1:
            self.load_page(0)
        elif operation == Operation.LOAD_PAGE_2:
            self.load_page(1)
        elif operation == Operation.LOAD_PAGE_3:
            self.load_page(2)
        elif operation == Operation.GO_BACK:
            self.go_back()
        elif operation == Operation.ADD_DIGEST:
            self.add_digest(*args, **kwargs)
        elif operation == Operation.PAGE_DOWN:
            self.page_down()
        elif operation == Operation.PAGE_UP:
            self.page_up()
        elif operation == Operation.TO_TOP:
            self.return_top()
        elif operation == Operation.MERGE:
            self.merge(*args, **kwargs)
        elif operation == Operation.END:
            self.end()
        elif operation == Operation.REJECT:
            pass
        else:
            raise Exception('Invalid Operation.')

    def fork(self, replicas):
        """Copy current status and return list of driver replicas.

        Keyword arguments:

        replicas -- number of replicas
        """
        start_time = time.time()
        status_list = [self]
        for _ in range(replicas-1):
            # status_list.append(Operator(self.topic, self.content.copy(), self.digests.copy(), self.curResultChunk, self.curTargetPageResultChunk))
            status_list.append(copy.deepcopy(self))
        print(f'fork time:{time.time() - start_time}s')
        return status_list
        

    def start(self, topic=None):
        """Start interact.

        Keyword arguments:

        topic -- topic name, default 'none'
        """
        self.topic = topic


    def search(self, key_words, filter=None) -> list:
        """Search key_words, return a list of class SearchResult.

        Keyword arguments:

        key_words -- key words want to search

        filter -- list of domains want to ignore
        """
        start_time = time.time()

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
        def _search(key_words):
            result = requests.get(endpoint, headers=headers, params={'q': key_words, 'mkt': mkt }, timeout=10)
            if result.status_code == 200:
                result = result.json()

                self.content = []
                self.content.append(ContentItem(CONTENT_TYPE.SEARCH_RESULT, result["webPages"]["value"]))
                self.curResultChunk = 0
            else:
                raise Exception('Platform search error.')

        _search(key_words)

        print(f'search query: {key_words}, time consumed: {time.time() - start_time}s')

    def get_page_num(self) -> int:
        return len(self.content[-1].data)

    def load_page(self, idx:int) -> str:
        """Load page detail and return as str.

        Keyword arguments:

        idx -- index of the search result, need to be number in [0,1,2]
        """
        start_time = time.time()
        top = self.content[-1].data
        res = requests.get(top[idx]['url'], timeout=10)
        try:
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            content = res.text
            soup = BeautifulSoup(content, 'html.parser')
            text = trafilatura.extract(soup.prettify())
        except:
            text = ""
            print("the connection to the url is failed, nothing extracted")

        # print('content:', text)

        chunk = []
        if len(text) != 0:
            for i in range(math.ceil(len(text) / RESULT_TARGET_PAGE_PER_TEXT_COUNT)):
                chunk.append(text[i*RESULT_TARGET_PAGE_PER_TEXT_COUNT: (i+1)*RESULT_TARGET_PAGE_PER_TEXT_COUNT].strip())
        else:
            chunk.append('无内容')
        self.content.append(ContentItem(CONTENT_TYPE.RESULT_TARGET_PAGE, chunk))
        self.curTargetPageResultChunk = 0
        
        print(f'load time:{time.time() - start_time}s')
        return top[idx]['url'], text

    def go_back(self):
        """Back to last page."""
        if len(self.content) != 0:
            self.content.pop()

    def page_down(self) -> bool:
        '''Page down. When page num is 1, return False.'''
        top = self.content[-1].data

        if self._isSearchResultPage():
            if self.curResultChunk < math.ceil(len(top) / SEARCH_RESULT_LIST_CHUNK_SIZE) - 1:
                self.curResultChunk += 1
                return True
            else:
                return False
        elif self._isResultContentPage():
            if self.curTargetPageResultChunk < len(top) - 1:
                self.curTargetPageResultChunk += 1
                return True
            else:
                return False

        
    def page_up(self) -> bool:
        '''Page up. When page num is total num, return False.'''
        if self._isSearchResultPage():
            if self.curResultChunk > 0:
                self.curResultChunk -= 1
                return True
            else:
                return False
        elif self._isResultContentPage():
            if self.curTargetPageResultChunk > 0:
                self.curTargetPageResultChunk -= 1
                return True
            else:
                return False


    def return_top(self):
        """Return top"""
        if self._isSearchResultPage():
            self.curResultChunk = 0
        elif self._isResultContentPage():
            self.curTargetPageResultChunk = 0


    def add_digest(self, content):
        """Add digest.

        Keyword arguments:

        content -- content of the digest
        """
        self.digests.append([{'desc': content, 'chunkIndex': self.curTargetPageResultChunk}])
        

    def merge(self, idxes: list):
        """Merge digests.
        
        Keyword arguments:
        
        idxes -- index of digests, use list"""
        idxes = list(set(idxes))
        for i in range(len(idxes)):
            if idxes[i] < 0:
                idxes[i] += len(self.digests)
        idxes.sort()
        if idxes[-1] < len(self.digests):
            for i in range(1, len(idxes)):
                out = self.digests.pop(idxes[i] - i + 1)
                for item in out:
                    self.digests[idxes[0]].append(item)

        

    def end(self):
        """End interact."""
        pass
        
    def get_all_page_detail(self):
        top = self.content[-1].data
        return top


    def get_page_detail(self):
        """Get page detail.

        When the page is detail page, return the detail as str. 

        When the page is search page, return a list of search result. Format:

        [
            {"title": "xxxxxxxxxx", "href": "https://xxxxxxxxx", "summary": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"},

            {"title": "xxxxxxxxxx", "href": "https://xxxxxxxxx", "summary": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"},

            {"title": "xxxxxxxxxx", "href": "https://xxxxxxxxx", "summary": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
        ]
        """
        top = self.content[-1].data
        if self._isSearchResultPage():
            start_idx = self.curResultChunk*SEARCH_RESULT_LIST_CHUNK_SIZE
            end_idx = start_idx + SEARCH_RESULT_LIST_CHUNK_SIZE \
                        if SEARCH_RESULT_LIST_CHUNK_SIZE <= len(top[start_idx:]) \
                        else start_idx + len(top[start_idx:])
            output_data = top[start_idx: end_idx]
            return [{"title": item["name"], "href": item["url"], "summary": item["snippet"]} for item in output_data]
        elif self._isResultContentPage():
            return top[self.curTargetPageResultChunk]

    def get_digests(self):
        """Get digests.

        Return a list of digests. Format:

        [
            [
                {"desc": "xxxxxxxxxx", "chunkIndex": 0},

                {"desc": "xxxxxxxxxxxxxxxxx", "chunkIndex": 1}
            ],

            [
                {"desc": "xxxxxxxxxxxxxxxxxxx", "chunkIndex": 0}
            ]
        ]
        """
        return self.digests