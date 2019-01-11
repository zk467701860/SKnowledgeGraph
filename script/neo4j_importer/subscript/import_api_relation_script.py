from neo4j_importer.import_api_relation import APIRelationImporter
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor

if __name__ == "__main__":
    # import relationships automatically
    api_relation_importer = APIRelationImporter()
    graphClient = APIGraphAccessor(GraphClient(server_number=4))
    api_relation_importer.start_import(graphClient)
