from py2neo import Relationship

from db.engine_factory import EngineFactory
from db.model import APIRelation, APIEntity
from shared.logger_util import Logger


class APIRelationImporter:
    def __init__(self):
        self.logger_file_name = "import_api_relation_to_neo4j"
        self.logger = None
        self.graphClient = None
        self.session = None

    def start_import(self, graphClient):
        self.logger = Logger(self.logger_file_name).get_log()
        if not self.session:
            self.session = EngineFactory.create_session()
        self.graphClient = graphClient
        all_relation_list = self.session.query(APIRelation).all()
        for api_relation in all_relation_list:
            self.import_one_relation(api_relation)
        print("import api entity relation complete")

    def import_one_relation(self, api_relation):
        if api_relation is not None:
            relation_type = APIRelation.get_type_string(api_relation.relation_type)
            start_api_id = api_relation.start_api_id
            end_api_id = api_relation.end_api_id
            start_node = self.graphClient.find_node_by_api_id(start_api_id)
            end_node = self.graphClient.find_node_by_api_id(end_api_id)
            if start_node is not None and end_node is not None:
                if relation_type == "belong to":
                    relation_type = self.transfer_belong_to_type(start_api_id)
                    relationship = Relationship(end_node, relation_type, start_node)
                    self.graphClient.graph.merge(relationship)
                else:
                    relationship = Relationship(start_node, relation_type, end_node)
                    self.graphClient.graph.merge(relationship)
                self.logger.info("create or merge relation" + str(relationship))
            else:
                self.logger.warn("fail create relation because start node or end node is none.")
        else:
            self.logger.warn("fail create relation because api relation is none.")

    def transfer_belong_to_type(self, start_api_id):
        if start_api_id is not None:
            start_api_entity = APIEntity.find_by_id(self.session, start_api_id)
            if start_api_entity is not None:
                start_api_type = start_api_entity.api_type
                type_str = APIEntity.get_simple_type_string(start_api_type)
                type_str = type_str.replace("api", "")
                relation_str = "has" + type_str
                return relation_str
        return None
