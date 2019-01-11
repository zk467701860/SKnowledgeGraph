from db.engine_factory import EngineFactory
from db.model import APIEntity, APIDocumentWebsite
from shared.logger_util import Logger


class APIDocumentWebsiteImporter:
    def __init__(self):
        self.logger_file_name = "import_api_document_website_to_neo4j"
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
            api_id = api_entity.id
            api_document_website_list = APIDocumentWebsite.get_document_website_list_by_api_id(self.session, api_id)
            self.import_document_website_to_one_entity(api_id, api_document_website_list)

        print("import api doc url complete")

    def import_document_website_to_one_entity(self, api_id, api_document_website_list):
        if api_id is not None and api_document_website_list is not None:
            node = self.graphClient.find_node_by_api_id(api_id)
            if node is not None:
                index = 1
                for each in api_document_website_list:
                    website = each[0]
                    key = "api_document_website#" + str(index)
                    index += 1
                    if key not in dict(node).keys():
                        node[key] = website
                self.graphClient.push_node(node)
                self.logger.info("add document website property " + str(node))
            else:
                self.logger.warn("fail to add document property because node is none")
        else:
            self.logger.warn("fail to add document property because api id is none")
