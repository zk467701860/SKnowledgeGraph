import random


from extractor import WikiDataItemSelector
from extractor import WikiDataRelationLinker
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_wikidata import \
    WikiDataGraphAccessor

if __name__ == '__main__':
    graph_client = WikiDataGraphAccessor(GraphClient(server_number=1))
    linker = WikiDataRelationLinker(graphClient=graph_client)
    selector = WikiDataItemSelector()
    item_id_list = selector.get_wikidata_item_id_list()
    random.shuffle(item_id_list)
    linker.link_relation_for_wikidata_items(*item_id_list)
