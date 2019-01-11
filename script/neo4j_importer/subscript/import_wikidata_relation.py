from neo4j_importer.wikidata_relation_linker import WDRelationLinker
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    client = GraphClient(server_number=4)
    linker = WDRelationLinker(graph_client=client)
    linker.start_link()
    print("unlink relation number=%d", linker.unlink_relation)
    # linker.link_relation_for_wikidata_node_by_wd_item_id("Q681524")
