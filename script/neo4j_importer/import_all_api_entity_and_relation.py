from neo4j_importer.import_all_api_entity import AllAPIEntityImporter
from neo4j_importer.import_api_document_website import APIDocumentWebsiteImporter
from neo4j_importer.import_api_relation import APIRelationImporter
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor

if __name__ == "__main__":
    graphClient = APIGraphAccessor(GraphClient(server_number=4))

    api_entity_importer = AllAPIEntityImporter()
    api_entity_importer.start_import(graphClient)

    api_relation_importer = APIRelationImporter()
    api_relation_importer.start_import(graphClient)

    api_document_website_importer = APIDocumentWebsiteImporter()
    api_document_website_importer.start_import(graphClient)
