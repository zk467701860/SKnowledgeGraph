from unittest import TestCase

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.node_cleaner import NodeRelationFilter


class TestNodeRelationFilter(TestCase):
    def setUp(self):
        self.graphClient = DefaultGraphAccessor(GraphClient())
        self.filter = NodeRelationFilter()

    def test_check_node_validity(self):
        result_list = [(70382, True),
                       (243657, False),
                       (429132, True),
                       (244468, False)]
        for case in result_list:
            node = self.graphClient.find_node_by_id(case[0])
            print(node)
            self.assertEqual(self.filter.check_node_validity(node), case[1])

    def test_check_node_name_validation(self):
        self.fail()

    def test_judge_node_source_validation(self):
        pass

    def test_check_relation_validity(self):
        pass

    def test_filter_subgraph(self):
        result_list = [
            (276157, True, 8, 7),
            (92836, True, 9, 8),
        ]
        for case in result_list:
            subgraph = self.graphClient.expand_node_for_adjacent_nodes_to_subgraph(case[0])
            print(subgraph)
            filter_subgraph = self.filter.filter_subgraph(subgraph)

            if case[1] == True:
                self.assertIsNotNone(filter_subgraph)
                self.assertEqual(len(filter_subgraph.nodes()), case[2])
                self.assertEqual(len(filter_subgraph.relationships()), case[3])

            else:
                self.assertIsNone(filter_subgraph)

    def test_filter_relations(self):
        self.fail()

    def test_filter_nodes(self):
        self.fail()
