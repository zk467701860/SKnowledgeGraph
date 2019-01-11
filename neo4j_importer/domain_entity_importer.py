from db.engine_factory import EngineFactory
from db.model import DomainEntity, DomainEntityExtractFromSentenceRelation
from shared.logger_util import Logger
from skgraph.graph.accessor.graph_client_for_domain_entity import DomainEntityAccessor


class DomainEntityImporter:
    def __init__(self):
        self.logger_file_name = "import_domain_entity_to_neo4j"
        self.logger = None
        self.domain_entity_accessor = None
        self.session = None

    def init_importer(self, graph_client):
        self.domain_entity_accessor = DomainEntityAccessor(graph_client)
        self.logger = Logger(self.logger_file_name).get_log()
        if not self.session:
            self.session = EngineFactory.create_session()

    def start_import_all_domain_entity(self):
        domain_entity_list = DomainEntity.get_all_domain_entity_id_and_name(session=self.session)
        for domain_entity in domain_entity_list:
            self.domain_entity_accessor.create_or_update_domain_entity(domain_entity_id=domain_entity.id,
                                                                       name=domain_entity.name)

    def clean_kg_by_remove_all_domain_entity(self):
        self.domain_entity_accessor.delete_all_domain_entity_and_relation()

    def start_import_all_domain_entity_extract_from_relation(self):
        max_relation_id = DomainEntityExtractFromSentenceRelation.get_max_id(self.session)

        start_id = 0
        step = 10000
        for current_start_id in range(start_id, max_relation_id, step):
            current_end_id = current_start_id + step
            print("import relation, current start id=%d", current_start_id)
            all_relation_list = self.session.query(DomainEntityExtractFromSentenceRelation).filter(
                DomainEntityExtractFromSentenceRelation.id > current_start_id,
                DomainEntityExtractFromSentenceRelation.id <= current_end_id).all()
            for relation in all_relation_list:
                self.domain_entity_accessor.build_relation_for_domain_entity_to_sentence(
                    sentence_id=relation.sentence_id,
                    domain_entity_id=relation.domain_entity_id)

    def start_import_all_domain_entity_extract_by_domain_entity_step(self, start_domain_entity_id,
                                                                     end_domain_entity_id):
        count = 0
        for domain_entity_id in range(start_domain_entity_id, end_domain_entity_id):
            domain_entity = self.domain_entity_accessor.find_domain_entity_node_by_id(domain_entity_id)
            if domain_entity is None:
                continue
            all_relation_list = DomainEntityExtractFromSentenceRelation.get_all_relation_by_domain_entity_id(
                session=self.session,domain_entity_id=domain_entity_id)

            for relation in all_relation_list:
                self.domain_entity_accessor.build_relation_for_domain_entity_to_sentence_with_start_node(
                    sentence_id=relation.sentence_id,
                    domain_entity=domain_entity)
            count = count + 1
            if count >= 1000:
                count = 0
                print("domain_entity_id=%d" % domain_entity_id)
