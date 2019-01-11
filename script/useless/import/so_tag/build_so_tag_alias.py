import codecs
import json


from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_so_tag import SOTagGraphAccessor

graphClient = SOTagGraphAccessor(GraphClient(server_number=5))
file_name = "clean_tag_json.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    tag_data = json.load(f)
for tag_entity in tag_data:
    name = tag_entity["TagName"]
    url = tag_entity["url"]
    node = graphClient.find_so_tag_by_url(tag_url=url)
    if node is not None:
        alias = []
        if "alias" in node.keys():
            alias = node["alias"]
        alias.append(name)
        alias.append(name.replace("-", " "))
        alias = list(set(alias))
        node["alias"] = alias
        graphClient.push(node)
    print name + " get"

file_name = "tag_synonyms_entity.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    tag_data = json.load(f)
for tag_entity in tag_data:
    name = tag_entity["TagName"]
    url = tag_entity["url"]
    node = graphClient.find_so_tag_by_url(tag_url=url)
    if node is not None:
        alias = []
        if "alias" in node.keys():
            alias = node["alias"]
        alias.append(name)
        alias.append(name.replace("-", " "))
        alias = list(set(alias))
        node["alias"] = alias
        graphClient.graph.push(node)
    print name + " get"
