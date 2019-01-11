from neo4j_importer.init_graph_index import GraphIndexInit
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    index_initor = GraphIndexInit(graph_client=GraphClient(server_number=4))
    index_initor.init_graph_index()
