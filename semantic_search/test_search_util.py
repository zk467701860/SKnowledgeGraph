from unittest import TestCase

from db.engine_factory import EngineFactory
from db.search import APISearcher
from semantic_search.semantic_search_util_for_api import APISentenceLevelSemanticSearch
from server_util.search import SearchUtil
from skgraph.graph.accessor.graph_accessor import GraphClient


class TestSearchUtil(TestCase):
    def test_search(self):
        api_entity_session = EngineFactory.create_session(autocommit=True)
        api_searcher = APISearcher(session=api_entity_session, )

        graph_client = GraphClient(server_number=4)
        api_semantic_searcher = APISentenceLevelSemanticSearch()
        api_semantic_searcher.init()
        search_util = SearchUtil(graph_client, api_searcher,api_semantic_searcher)
        result = search_util.search("string buffer", 10)
        print(result)
        self.assertEqual(len(result), 10)