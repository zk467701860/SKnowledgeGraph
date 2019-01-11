#!/usr/bin/python
# -*- coding: UTF-8 -*-

from unittest import TestCase

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.node_cleaner import NodeCleaner, PUBLIC_LABELS
from skgraph.util.data_clean_util import construct_property_set, rename_property


class TestNodeCleaner(TestCase):
    def test_clean_labels(self):
        self.graphClient = DefaultGraphAccessor(GraphClient(server_number=1))

        node = self.graphClient.find_node_by_id(16)
        self.assertEqual(NodeCleaner.clean_labels(node), [u'software', u'background knowledge', u'WikiData'])
        node = self.graphClient.find_node_by_id(177777)
        print node
        self.assertEqual(NodeCleaner.clean_labels(node), [u'background knowledge', u'WikiData'])

    def test_construct_property_set(self):
        node_list = [{"aaa": 1, "ccc": 6}, {"aaa": 2, "bbb": 3, "ccc": 6}, {"ccc": 4, "ddd": 5}]
        result = {"aaa", "ccc"}
        self.assertEqual(construct_property_set(node_list), result)
        print construct_property_set(node_list)

    def test_rename_property(self):
        self.graphClient = DefaultGraphAccessor(GraphClient(server_number=0))
        node_list = self.graphClient.find_by_name_property("awesome item", "acl9")
        result = rename_property(node_list)
        print result

    def test_public_labels_name(self):
        t = PUBLIC_LABELS
        self.assertIsNotNone(t)
        print(t)
