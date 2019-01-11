import random

import gevent

from extractor import WikiDataNodeCreator
from extractor import WikiDataItem
from extractor import WikiDataItemSelector
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_wikidata import \
    WikiDataGraphAccessor


def get_wd_item(wd_item_id):
    return WikiDataItem(wd_item_id)


if __name__ == '__main__':

    thread_num = 12
    graphClient = WikiDataGraphAccessor(GraphClient(server_number=1))
    creator = WikiDataNodeCreator(graphClient=graphClient)
    selector = WikiDataItemSelector()
    item_id_list = selector.get_wikidata_item_id_list()
    random.shuffle(item_id_list)

    # split the id list
    split_item_id_list = [item_id_list[i:i + thread_num] for i in range(0, len(item_id_list), thread_num)]

    for group_item_id_list in split_item_id_list:
        jobs = []
        for item_id in group_item_id_list:
            jobs.append(gevent.spawn(get_wd_item, item_id))

        gevent.joinall(jobs, timeout=120)

        for job in jobs:
            item = job.value
            if not item:
                continue
            node = graphClient.find_wikidata_node(item.wd_item_id)
            if not node:
                creator.create_item_node_from_WikiDataItem_object(item)
            else:
                continue
