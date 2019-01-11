from db.engine_factory import EngineFactory
from db.model import APIEntity
from shared.logger_util import Logger
from skgraph.graph.accessor.factory import NodeBuilder


class AllAPIEntityImporter:
    def __init__(self):
        self.logger_file_name = "import_api_entity_to_neo4j"
        self.logger = None
        self.graphClient = None
        self.session = None

    def start_import(self, graphClient):
        self.logger = Logger(self.logger_file_name).get_log()
        if not self.session:
            self.session = EngineFactory.create_session()
        self.graphClient = graphClient

        all_apis = self.session.query(APIEntity).all()
        for api_entity in all_apis:
            self.import_one_api_entity(api_entity)
        print("import api entity complete")

    def import_one_api_entity(self, api_entity):
        api_type = APIEntity.get_simple_type_string(api_entity.api_type)
        print(api_type)
        property_dict = api_entity.__dict__
        property_dict.pop("_sa_instance_state")
        property_dict["api_id"] = property_dict.pop("id")
        builder = NodeBuilder()
        builder.add_entity_label().add_property(**property_dict).add_api_label().add_label(api_type)

        node = builder.build()
        # when the node's qualifier name is "byte","int", the print will cause ValueError: Invalid identifier error
        # print node

        try:
            self.graphClient.create_or_update_api_node(node=node)
            self.logger.info('create node for api entity %s', property_dict['api_id'])
        except Exception, error:
            self.logger.warn('-%s- fail for create node for api entity ', property_dict['api_id'])
            self.logger.exception('this is an exception message')

