from unittest import TestCase

from db.engine_factory import EngineFactory
from db.search import GeneralConceptEntitySearcher


class TestGet_candidate_wiki_set(TestCase):

    def test_full_text_searcher(self):
        session = EngineFactory.create_session(autocommit=True)

        searcher = GeneralConceptEntitySearcher(session=session)
        result = searcher.search("apk file")
        print(len(result))
        print(result)
