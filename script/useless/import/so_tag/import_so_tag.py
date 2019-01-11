import codecs
import json

from py2neo import Relationship

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
    if node is None:
        node = graphClient.create_so_tag_by_url(tag_url=url, name=name)
    print name + " get"
    print node

file_name = "tag_synonyms_entity.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    tag_data = json.load(f)
for tag_entity in tag_data:
    name = tag_entity["TagName"]
    url = tag_entity["url"]
    node = graphClient.find_so_tag_by_url(tag_url=url)
    if node is None:
        node = graphClient.create_so_tag_by_url(tag_url=url, name=name)
    print name + " get"
    print node

file_name = "tag_synonyms_relation.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    tag_relation_data = json.load(f)
for tag_relation in tag_relation_data:
    start_url = tag_relation["start_url"]
    relation = tag_relation["relation"]
    end_url = tag_relation["end_url"]
    start_node = graphClient.find_so_tag_by_url(start_url)
    end_node = graphClient.find_so_tag_by_url(end_url)
    if start_node is not None and end_node is not None:
        graphClient.graph.merge(Relationship(start_node, relation, end_node))
