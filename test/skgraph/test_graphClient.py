#!/usr/bin/python
# -*- coding: UTF-8 -*-

from unittest import TestCase

from py2neo import Node

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.node_cleaner import NodeCleaner, GraphJsonParser


def count_record_list(record_list):
    count = 0
    for record in record_list:
        count = count + 1
    return count


class TestGraphClient(TestCase):
    graphClient = None

    def setUp(self):
        self.graphClient = DefaultGraphAccessor(GraphClient())
        self.nodeCleaner=NodeCleaner()

    def test_get_max_id_for_node(self):
        self.assertEqual(self.graphClient.get_max_id_for_node(), 697753)

    def test_get_adjacent_node_id_list(self):
        self.assertEqual(self.graphClient.get_adjacent_node_id_list(66666666), [])

        correct = [64289, 52628, 62565]

        self.assertEqual(self.graphClient.get_adjacent_node_id_list(7899), correct)

    def test_get_node_name_by_id(self):
        self.assertEqual(self.graphClient.get_node_name_by_id(66666666), None)
        self.assertEqual(self.graphClient.get_node_name_by_id(3444), "Adobe Device Central")

    def test_expand_node_for_directly_adjacent_nodes_to_subgraph(self):
        # self.assertEqual(self.graphClient.expand_node_for_adjacent_nodes_to_subgraph(3444),
        #                  "Adobe Device Central")
        pass

    def test_find_by_alias_name_property_exactly_match_from_label_limit_one(self):
        self.assertEqual(self.graphClient.find_one_by_alias_name_property("entity", "Adobe Device Central"), None)
        interface = self.graphClient.find_one_by_alias_name_property("api", "Interface PrintGraphics")
        self.assertEqual(93008, self.graphClient.get_id_for_node(interface))

    def test_find_by_alias_name_property(self):
        self.assertEqual(self.graphClient.find_by_alias_name_property("entity", "Adobe Device Central"), [])
        interfaces = self.graphClient.find_by_alias_name_property("api", "Interface PrintGraphics")
        self.assertEqual(len(interfaces), 1)
        self.assertEqual(93008, self.graphClient.get_id_for_node(interfaces[0]))

    def test_get_relation_by_relation_id(self):
        relation = self.graphClient.get_relation_by_relation_id(470129)
        self.assertIsNone(relation)

        relation = self.graphClient.get_relation_by_relation_id(122211)

        self.assertEqual(122211, self.graphClient.get_id_for_node(relation))
        self.assertEqual(91, self.graphClient.get_id_for_node(relation.start_node()))
        self.assertEqual(29390, self.graphClient.get_id_for_node(relation.end_node()))

        subgraph = self.graphClient.get_relations_between_two_nodes_in_subgraph(246029, 246030)
        relations_json = []
        for r in subgraph.relationships():
            r = {
                "id": self.graphClient.get_id_for_node(relation),
                "name": relation.type(),
                "start_id": self.graphClient.get_start_id_for_relation(relation),
                "end_id": self.graphClient.get_end_id_for_relation(relation)
            }
            print r
        subgraph = self.graphClient.get_relations_between_two_nodes_in_subgraph(246029, 246033)
        self.assertEqual(subgraph, None)

    def test_find_node_by_id(self):
        node = self.graphClient.find_node_by_id(5444)
        self.assertEqual(5444, self.graphClient.get_id_for_node(node))

    def test_search_nodes_by_name(self):
        nodes = self.graphClient.search_nodes_by_name("java")
        count = 0
        for n in nodes:
            count = count + 1
        self.assertEqual(10, count)

        nodes = self.graphClient.search_nodes_by_name("String buffer()")

        count = 0
        for n in nodes:
            count = count + 1
        self.assertEqual(10, count)

    def test_search_nodes_by_name_in_subgraph(self):
        subgraph = self.graphClient.search_nodes_by_name_in_subgraph("java")
        count = 0
        for n in subgraph.nodes():
            count = count + 1
        self.assertEqual(10, count)

        subgraph = self.graphClient.search_nodes_by_name_in_subgraph("String buffer()")
        count = 0
        if subgraph is not None:
            for n in subgraph.nodes():
                count = count + 1
        self.assertEqual(10, count)

    def test_get_relations_between_two_nodes_in_subgraph(self):
        subgraph = self.graphClient.get_relations_between_two_nodes_in_subgraph(48, 3600)
        self.assertEqual(None, subgraph)

        subgraph = self.graphClient.get_relations_between_two_nodes_in_subgraph(48, 3643)

        self.assertEqual(2, len(subgraph.nodes()))
        self.assertEqual(1, len(subgraph.relationships()))

    def test_get_relations_between_two_nodes(self):
        record_list = self.graphClient.get_relations_between_two_nodes(48, 3600)
        count = 0
        for n in record_list:
            count = count + 1
        self.assertEqual(0, count)

        record_list = self.graphClient.get_relations_between_two_nodes_in_subgraph(48, 3643)

        count = 0
        for n in record_list:
            count = count + 1

        self.assertEqual(1, count)

    def test_cleaner(self):
        node = self.graphClient.find_node_by_id(444)
        self.assertEqual(self.nodeCleaner.get_clean_node_name(node), "fake news")

        node = self.graphClient.find_node_by_id(4444)
        self.assertEqual(self.nodeCleaner.get_clean_node_name(node), "")

        self.assertEqual(self.graphClient.get_id_for_node(Node("lll", a=3)), -1)
        self.assertEqual(self.graphClient.get_id_for_node(node), 4444)

    def test_get_shortest_path_to_name(self):
        name = self.graphClient.get_node_name_by_id(8000)
        subraph = self.graphClient.get_shortest_path_to_name_in_subgraph(444, name)
        print subraph

    def test_get_shortest_path(self):
        record_list = self.graphClient.get_shortest_path(444, 8000, max_degree=2)
        self.assertEqual(0, count_record_list(record_list))

        record_list = self.graphClient.get_shortest_path(444, 8000)
        self.assertNotEqual(None, record_list)
        self.assertEqual(1, count_record_list(record_list))

        subgraph = self.graphClient.get_shortest_path_in_subgraph(444, 8000, max_degree=2)
        self.assertEqual(None, subgraph)

        subgraph = self.graphClient.get_shortest_path_in_subgraph(444, 8000, max_degree=6)
        self.assertNotEqual(None, subgraph)
        self.assertEqual(len(subgraph.nodes()), 7)
        self.assertEqual(len(subgraph.relationships()), 6)
        print subgraph

    def test_get_newest_nodes(self):
        node_list = self.graphClient.get_newest_nodes(10)
        self.assertEqual(10, len(node_list))
        print(node_list)
        graphJsonParser = GraphJsonParser()
        returns = graphJsonParser.parse_node_list_to_json(node_list)
        print(returns)

