from unittest import TestCase

from sqlalchemy import func

from db.engine_factory import EngineFactory
from db.model import SentenceToAPIEntityRelation


class TestDocumentSentenceImporter(TestCase):
    def test_start_import_all_valid_sentences(self):
        session = EngineFactory.create_session()
        max_relation_id = session.query(func.max(SentenceToAPIEntityRelation.id)).scalar()
        print(max_relation_id)
