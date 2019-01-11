from google_seach.gsearch.googlesearch import search
from google_seach import textrank
from db.search import APISearcher,DocumentSearcher

import urllib2
from gzip import GzipFile
from StringIO import StringIO
import zlib
import re
from pyquery import PyQuery as pq


# class APIDocSummary():
#     def __init__(self, api_searcher=None, doc_searcher=None):
#         if not api_searcher:
#             self._api_searcher = APISearcher()
#         else:
#             self._api_searcher = api_searcher
#
#         # self._doc_searcher = not doc_searcher?DocumentSearcher:doc_searcher
#
#     def search_api_doc_from_qualified_name(name):
#         [(api_id, api_type)] = self.api_searcher..search_api_id_by_qualified_name(api_name=name)
#         document = DocumentSearcher.search_api_document_by_id(api_id)


class SummaryExtraction:
    def __init__(self):
        pass

    def summary_extraction(self, query_text, api_type, page_limit=10):
        _type = {"java": 'site:docs.oracle.com/javase/8/docs/ ',
                 "android": 'site:developer.android.com ',
                 "general": ""
                 }
        page_list = self.search_from_google(_type[api_type]+query_text, page_limit)
        result = []
        for page in page_list:
            try:
                page_data = {}
                page_data["tittle"] = page[0]
                page_data["url"] = page[1]
                print(page[0])
                print(page[1])
                summary = self.web_page_summary(page[1])
                print(summary)
                page_data["summary"] = summary
                result.append(page_data)
            except Exception, e:
                print(e)
        if len(result) > 10:
            return result[0:page_limit]
        else:
            return result

    @staticmethod
    def get_summary(text):
        return textrank.extract_sentences(text)

    @staticmethod
    def search_from_google(text, page_limit=10):
        result = search(text, num_results=page_limit+10)
        return result

    def web_page_summary(self, url):
        data = self.web_page_data(url)
        p = pq(data)
        sentence = p('p')
        print([i.text() for i in sentence.items('p')])
        text = re.sub('[<>/]', '', " ".join([i.text() for i in p.items('p')]))
        return self.get_summary(text)

    def web_page_data(self, url):
        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip,deflate')
        response = urllib2.urlopen(request)
        content = response.read()
        encoding = response.info().get('Content-Encoding')
        if encoding == 'gzip':
            content = self.gzip(content)
        elif encoding == 'deflate':
            content = self.deflate(content)
        return content

    @staticmethod
    def gzip(data):
        buf = StringIO(data)
        f = GzipFile(mode='rb', fileobj=buf)
        return f.read()

    @staticmethod
    def deflate(data):
        try:
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            return zlib.decompress(data)


# if __name__ == "__main__":
#     se = SummaryExtraction()
#     query_text = "python"
#     java_re = se.summary_extraction(query_text,"java", 10, False)
#     print(java_re)
#     android_re = se.summary_extraction(query_text,"android", 10, False)
#     print(android_re)
