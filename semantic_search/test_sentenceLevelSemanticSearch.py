from unittest import TestCase

from semantic_search.semantic_search_util import SentenceLevelSemanticSearch


class TestSentenceLevelSemanticSearch(TestCase):
    def test_search_entity_by_fulltext(self):
        searcher = SentenceLevelSemanticSearch()
        searcher.init()
        result = searcher.search_entity_by_fulltext(["image", "buffer", "file", "image file"])
        result.start_create_node_info_collection()
        result.print_informat()
        print(result)
