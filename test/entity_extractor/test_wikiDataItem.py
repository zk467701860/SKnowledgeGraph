from unittest import TestCase

from extractor.wikidata.WikiDataItem import WikiDataItem


class TestWikiDataItem(TestCase):
    def test_get_en_wiki_title(self):
        item=WikiDataItem(wd_item_id=None,init_at_once=False)
        item.init_wikidata_item_from_wikipedia_url(wikipedia_url="https://en.wikipedia.org/wiki/KNKC-LD")
        print(item.get_en_wiki_title())
