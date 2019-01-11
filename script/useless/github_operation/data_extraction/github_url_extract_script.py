import json

from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.node_collection import NodeCollection

node_collection = NodeCollection(GraphClient(server_number=0))
node_list = node_collection.get_all_nodes(1000, ['awesome item'])
print len(node_list)

github_url_list = []

for node in node_list:
    #print dict(node).keys()
    property_list = dict(node).keys()
    if "url" in property_list:
        github_url = node['url']
        if "github.com" in github_url:
            github_url_list.append(github_url)

result = []
for each in github_url_list:
    data_dict = {}
    data_dict.setdefault("id", github_url_list.index(each) + 1)
    data_dict.setdefault("github_url", each)
    result.append(data_dict)

with open("github_data.json", 'w') as f:
    json.dump(result, f)