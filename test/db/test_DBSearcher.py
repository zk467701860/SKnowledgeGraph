from unittest import TestCase
import unittest
from db.engine_factory import EngineFactory
from db.model import APIAlias, APIEntity
from db.search import SOPostSearcher, DBSearcher, APISearcher, SentenceSearcher
from semantic_search.semantic_search_util import QA_FullText_EntityList

class TestDBSearcher(TestCase):
    def test_full_text_search_for_os_answer(self):
        session = EngineFactory.create_session()
        searcher = SentenceSearcher(session)
        result = searcher.search_sentence_answer("java", 10)
        print(result)
        for line in result:
            print(line)
        self.assertEqual(10, len(result))

    def test_full_text_search_for_domain_qa(self):
        session = EngineFactory.create_session()
        searcher = QA_FullText_EntityList(session)
        result = searcher.search_related_entity("java", 10)
        print(result)
        for line in result:
            print(line)
        self.assertEqual(10, len(result))

    def test_full_text_search_in_nature_language_for_alias(self):
        session = EngineFactory.create_session()
        searcher = DBSearcher(session)
        result = searcher.full_text_search_in_nature_language("Json", APIAlias)
        for alias in result:
            print(alias)
        self.assertEqual(19, len(result))

    def test_search_POST(self):
        session = EngineFactory.create_so_session()
        searcher = SOPostSearcher(session)
        result = searcher.search_post("Json", 20)
        for post in result:
            print(post)
        self.assertEqual(20, len(result))

    def test_search_post_in_simple_format(self):
        session = EngineFactory.create_so_session()
        searcher = SOPostSearcher(session)
        result = searcher.search_post_in_simple_format("Json", 20)
        for post in result:
            print(post)
            print(post["id"])
            print(post["score"])
            print(post["title"])

        self.assertEqual(20, len(result))

    def test_API_aliases_searcher(self):
        session = EngineFactory.create_session()
        searcher = APISearcher(session)
        result = searcher.search_api_aliases("XML")
        for post in result:
            print(post)

        self.assertEqual(500, len(result))

    def test_API_entity_searcher(self):
        session = EngineFactory.create_session()
        searcher = APISearcher(session)
        result = searcher.search_api_entity("XML", result_limit=20)
        for api in result:
            print(api)

        self.assertEqual(20, len(result))

    def test_API_entity_searcher_in_tuple(self):
        session = EngineFactory.create_session()
        searcher = APISearcher(session)
        all_query_tuple = [
            ("XML", APIEntity.API_TYPE_ALL_API_ENTITY, 427),
            ("json",
             APIEntity.API_TYPE_ALL_API_ENTITY, 10),
            ("http", APIEntity.API_TYPE_METHOD, 31),
        ]
        for query, api_type, size in all_query_tuple:
            result = searcher.search_api_entity(query, api_type=api_type)
            for api_entity in result:
                print(api_entity)

            self.assertEqual(size, len(result))

    def test_API_entity_searcher_in_tuple_by_limit(self):
        session = EngineFactory.create_session()
        searcher = APISearcher(session)
        all_query_tuple = [
            ("XML", APIEntity.API_TYPE_ALL_API_ENTITY, 10,10),
            ("json",
             APIEntity.API_TYPE_ALL_API_ENTITY, 10,6),
            ("http", APIEntity.API_TYPE_METHOD, 20,20),
            ("java", APIEntity.API_TYPE_CLASS, 15, 0),

        ]
        for query, api_type, limit,size in all_query_tuple:
            result = searcher.search_api_entity(query, api_type=api_type,result_limit=limit)
            for api_entity in result:
                print(api_entity)

            self.assertEqual(size, len(result))

    def test_search_api_entity_by_id_list(self):
        session = EngineFactory.create_session()
        searcher = APISearcher(session)

        all_query_tuple = [
            ([1, 2, 3, 1111, 4444, 6666, 1], APIEntity.API_TYPE_ALL_API_ENTITY, 6),
            ([1, 2, 3, 4, 6, 7, 9, 1111, 4444, 6666, 1, 111, 444, 7777, 2345, 12222, 12222, 12225, 12227],
             APIEntity.API_TYPE_ALL_API_ENTITY, 17),
            ([1, 12222, 12225, 12227, 12228, 12220, 12229], APIEntity.API_TYPE_METHOD, 6),
        ]
        for query_id_list, api_type, size in all_query_tuple:
            result = searcher.query_api_entity(query_id_list, api_type)
            for api_entity in result:
                print(api_entity)

            self.assertEqual(size, len(result))

    def test_API_entity_searcher_in_tuple_by_limit_by_only_id(self):
        session = EngineFactory.create_session()
        searcher = APISearcher(session)
        all_query_tuple = [
            ("XML", APIEntity.API_TYPE_ALL_API_ENTITY, 10,10),
            ("json",
             APIEntity.API_TYPE_ALL_API_ENTITY, 10,10),
            ("http", APIEntity.API_TYPE_METHOD, 20,20),
            ("java", APIEntity.API_TYPE_CLASS, 15, 0),

        ]
        for query, api_type, limit,size in all_query_tuple:
            result = searcher.search_api_entity(query, api_type=api_type,result_limit=limit,result_format=APISearcher.RESULT_FORMAT_ONLY_ID)
            for api_entity in result:
                print(api_entity)

            self.assertEqual(size, len(result))

    def test_API_entity_searcher_for_large(self):
        session = EngineFactory.create_session()
        searcher = APISearcher(session)
        result = searcher.search_api_entity("Map", result_limit=20)
        for api in result:
            print(api)

        self.assertEqual(20, len(result))


if __name__ == "__main__":
    unittest.main()