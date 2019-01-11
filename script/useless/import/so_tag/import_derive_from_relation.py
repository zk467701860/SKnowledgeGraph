import codecs
import json

from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_so_tag import SOTagGraphAccessor

graphClient = SOTagGraphAccessor(GraphClient(server_number=5))

file_name = "tag_derive_relation.json"
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
        print "create"
    else:
        print tag_relation
