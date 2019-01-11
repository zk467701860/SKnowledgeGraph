from neo4j_importer.import_api_document_website import APIDocumentWebsiteImporter
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor

if __name__ == "__main__":
    # add document website property automatically
    api_document_website_importer = APIDocumentWebsiteImporter()
    graphClient = APIGraphAccessor(GraphClient(server_number=4))
    api_document_website_importer.start_import(graphClient)
