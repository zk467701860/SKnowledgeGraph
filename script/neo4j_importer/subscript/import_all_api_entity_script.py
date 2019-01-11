from neo4j_importer.import_all_api_entity import AllAPIEntityImporter
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor

if __name__ == "__main__":
    api_entity_importer = AllAPIEntityImporter()

    # import entities automatically
    graphClient = APIGraphAccessor(GraphClient(server_number=4))
    api_entity_importer.start_import(graphClient)


