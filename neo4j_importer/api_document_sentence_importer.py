import json

from sqlalchemy import func

from db.engine_factory import EngineFactory
from db.model import SentenceToAPIEntityRelation, DocumentSentenceText, DocumentSentenceTextAnnotation
from shared.logger_util import Logger
from skgraph.graph.accessor.graph_client_for_document_sentence import SentenceAccessor


class DocumentSentenceImporter:
    def __init__(self):
        self.logger_file_name = "import_document_sentence_to_neo4j"
        self.logger = None
        self.sentence_accessor = None
        self.session = None

    def init_importer(self, graph_client):
        self.logger = Logger(self.logger_file_name).get_log()
        if not self.session:
            self.session = EngineFactory.create_session()
        self.sentence_accessor = SentenceAccessor(graph_client)

    def start_import_all_first_sentence(self):
        all_sentence_entity_list = self.session.query(DocumentSentenceText).filter_by(sentence_index=0, valid=1).all()

        for sentence in all_sentence_entity_list:
            self.import_one_sentence_entity(sentence_id=sentence.id, sentence_text=sentence.text, sentence_type_code=
            DocumentSentenceTextAnnotation.ANNOTATED_TYPE_FUNCTIONALITY)

    def start_import_all_valid_sentences(self):
        all_sentence_entity_list = self.session.query(DocumentSentenceText).filter_by(valid=1).all()

        for sentence in all_sentence_entity_list:
            self.import_one_sentence_entity(sentence_id=sentence.id, sentence_text=sentence.text, sentence_type_code=
            DocumentSentenceTextAnnotation.ANNOTATED_TYPE_OTHERS)
        print("import sentences complete")

    def start_import_all_sentence_to_api_entity_relation(self):
        max_relation_id = self.session.query(func.max(SentenceToAPIEntityRelation.id)).scalar()

        start_id = 0
        step = 10000
        for current_start_id in range(start_id, max_relation_id, step):
            current_end_id = current_start_id + step
            print("import relation, current start id=%d", current_start_id)
            all_relation_list = self.session.query(SentenceToAPIEntityRelation).filter(
                SentenceToAPIEntityRelation.id > current_start_id,
                SentenceToAPIEntityRelation.id <= current_end_id).all()
            for relation in all_relation_list:
                self.sentence_accessor.build_relation_for_sentence_to_api(sentence_id=relation.sentence_id,
                                                                          api_id=relation.api_id)
        print("import sentences to api relation complete")

    def import_one_sentence_entity(self, sentence_id, sentence_text, sentence_type_code):
        self.sentence_accessor.create_or_update_sentence(sentence_id=sentence_id, sentence_text=sentence_text,
                                                         sentence_type_code=sentence_type_code)
        # print("import one sentence entity=%d", sentence_id)

    def import_sentence_type_from_json(self, json_file):
        with open(json_file, 'r') as f:
            link_relation_list = json.load(f)
        print("loading complete")
        type1 = 0
        type2 = 0
        type0 = 0
        for team in link_relation_list:
            sentence_id = team["sentence_id"]
            sentence_type_code = team["type"]
            if sentence_type_code == 0:
                type0 = type0 + 1
            if sentence_type_code == 1:
                type1 = type1 + 1
            if sentence_type_code == 2:
                type2 = type2 + 1
            self.sentence_accessor.update_sentence_type_code(sentence_id=sentence_id,
                                                             sentence_type_code=sentence_type_code)

        print("type0=%d" % type0)
        print("type1=%d" % type1)
        print("type2=%d" % type2)
