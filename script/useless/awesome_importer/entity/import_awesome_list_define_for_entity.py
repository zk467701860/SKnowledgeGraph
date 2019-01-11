import codecs
import json

from skgraph.graph.accessor.factory import NodeBuilder
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor

awesomeGraphAccessor = AwesomeGraphAccessor(GraphClient(server_number=0))
baseGraphClient = awesomeGraphAccessor.graph

file_name = "awesome_list_define_for_entity_list.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    awesome_item_category_entity_list = json.load(f)

for cate in awesome_item_category_entity_list:
    builder = NodeBuilder(). \
        add_label("awesome list topic"). \
        add_entity_label(). \
        add_one_property("name", cate)

    node = builder.build()
    print node
    node = baseGraphClient.merge(node)

## todo link different source to the same wikidata concept