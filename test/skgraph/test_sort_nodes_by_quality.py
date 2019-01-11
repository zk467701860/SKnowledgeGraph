from unittest import TestCase

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.node_cleaner import GraphJsonParser


class TestSort_nodes_by_quality(TestCase):
    def test_sort_nodes_by_quality(self):
        graphClient = DefaultGraphAccessor(GraphClient(server_number=1))
        graphJson = GraphJsonParser()
        keyword = "java"
        top_number = 10
        subgraph = graphClient.search_nodes_by_name_in_subgraph(keyword, top_number)
        print subgraph
        nodes = graphJson.parse_nodes_in_subgraph_to_public_json(subgraph)

        print nodes
