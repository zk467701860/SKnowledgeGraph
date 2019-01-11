from unittest import TestCase

from semantic_search.semantic_search_util import SentenceLevelSemanticSearch


class TestNode2VecModel(TestCase):
    def test_qa_model(self):
        qa = SentenceLevelSemanticSearch()
        text = "java language is a new way"
        chunk_list = qa.get_chunk_from_text(text)
        print(chunk_list)
        entity_list = qa.search_entity_by_fulltext(chunk_list)

        for entity in entity_list:
            print(entity)
        sentence_list = qa.search_sentence_by_entity_for_qa_list(entity_list)
        new_sentence_list = qa.sort_sentence_by_entities_as_bridge(text, sentence_list, entity_list)
        for sort_re in new_sentence_list:
            print(sort_re)
