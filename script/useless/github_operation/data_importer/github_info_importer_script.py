import codecs
import json

from py2neo import watch
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor

watch("httpstream")
awesomeGraphAccessor = AwesomeGraphAccessor(GraphClient(server_number=0))
baseGraphClient = awesomeGraphAccessor.graph

filename = "temp_data.json"
with codecs.open(filename, "r", "utf8") as f:
    github_info_list = json.load(f)
'''   
each = github_info_list[0]
github_url = each["github:url"]
node = awesomeGraphAccessor.find_awesome_item_by_url(github_url)
if node is not None:
        keys = each.keys()
        for key in keys:
            node[key] = each[key]
        print github_info_list.index(each) + 1
        print node
        awesomeGraphAccessor.push_node(node)
'''
for each in github_info_list:
    github_url = each["github:url"]
    node = awesomeGraphAccessor.find_awesome_item_by_url(github_url)
    if node is not None:
        keys = each.keys()
        for key in keys:
            if each[key] and key not in dict(node).keys():
                node[key] = each[key]
        print github_info_list.index(each) + 1
        print node
        awesomeGraphAccessor.push_node(node)
