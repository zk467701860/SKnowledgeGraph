import sys
from urllib import unquote

reload(sys)
sys.setdefaultencoding('utf-8')


class URLUtil:
    @staticmethod
    def parse_url_to_title(url):
        site_str = url.replace('https://en.wikipedia.org/wiki/', '')
        title = site_str.strip(" _").replace("_", " ").replace('"', "&quot;")
        title = unquote(str(title))
        return title
