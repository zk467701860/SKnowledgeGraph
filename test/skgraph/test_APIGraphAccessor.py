from unittest import TestCase

from py2neo import Node

from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor


class TestAPIGraphAccessor(TestCase):
    graphClient = None

    def setUp(self):
        self.graphClient = APIGraphAccessor(GraphClient())

    def test_get_parent_api_node_for_api_node(self):
        node = self.graphClient.get_parent_api_node_for_api_node(93013)
        self.assertEqual(type(node), Node)
        self.assertEqual(self.graphClient.get_id_for_node(node), 92919)
