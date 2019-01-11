import codecs
import json

from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor

awesomeGraphAccessor = AwesomeGraphAccessor(GraphClient(server_number=0))
baseGraphClient = awesomeGraphAccessor.graph

file_name = "new_complete_list_of_awesome_list.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    awesome_item_category_entity_list = json.load(f)
for cate in awesome_item_category_entity_list:
    property_dict = {
        "name": cate["name"],
        "category": cate["category"],
        "repository name": cate["repository name"],
        "alias": cate["alias"],
        "url": cate["url"],
        "source code repository": cate["url"]
    }
    if "description" in cate.keys() and cate["description"] != "":
        property_dict["description"] = cate["description"]

    node = awesomeGraphAccessor.create_or_update_awesome_list_entity(cate["url"], property_dict)

file_name = "awesome_item_category_entity_list.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    awesome_item_category_entity_list = json.load(f)
for cate in awesome_item_category_entity_list:
    node = awesomeGraphAccessor.find_or_create_awesome_cate(cate)

file_name = "awesome_list_cate_entity_list.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    awesome_item_category_entity_list = json.load(f)
for cate in awesome_item_category_entity_list:
    node = awesomeGraphAccessor.find_or_create_awesome_cate(cate)
