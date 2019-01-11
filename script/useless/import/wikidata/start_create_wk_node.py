import random


from extractor import WikiDataNodeCreator
from extractor import WikiDataItemSelector
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_wikidata import \
    WikiDataGraphAccessor

if __name__ == '__main__':
    graphAccessor = WikiDataGraphAccessor(GraphClient(server_number=1))
    creator = WikiDataNodeCreator(graphClient=graphAccessor)
    selector = WikiDataItemSelector()
    item_id_list = selector.get_wikidata_item_id_list()
    random.shuffle(item_id_list)
    creator.create_item_nodes(*item_id_list)
