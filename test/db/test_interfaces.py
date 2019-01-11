from unittest import TestCase

from db.engine_factory import EngineFactory
from db.model import DocumentSentenceTextAnnotation, DocumentText


class Test_interfaces(TestCase):

    def test_get_annotation_by_index(self):
        session = EngineFactory.create_session()
        annotation = DocumentSentenceTextAnnotation.get_annotation_count_by_index(session, 1, 1)
        expected = -1
        print annotation
        self.assertEqual(expected, annotation)

    def test_get_doc_id_list(self):
        session = EngineFactory.create_session()
        doc_id_list = DocumentText.get_doc_list(session)
        for each in doc_id_list:
            print each.id, " ", each.text

    def test_get_annotation_count_by_index(self):
        session = EngineFactory.create_session()
        annotation_count = DocumentSentenceTextAnnotation.get_annotation_count_by_index(session, 1, 1)
        expected = 1
        self.assertEqual(expected, annotation_count)