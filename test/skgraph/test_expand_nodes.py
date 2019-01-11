from unittest import TestCase

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.node_cleaner import GraphJsonParser


class TestGraphClient(TestCase):
    def setUp(self):
        self.graphClient = DefaultGraphAccessor(GraphClient())

    def test_expand_nodes(self):
        test_case = [(55730, True, 50, 50), (15555, True, 4, 4), (93008, True, 10, 11), (1708, True, 8, 7)]
        for node_id, is_valid, node_num, relation_num in test_case:
            subgraph = self.graphClient.expand_node_for_adjacent_nodes_to_subgraph(node_id)
            if is_valid:
                self.assertIsNotNone(subgraph)
            else:
                self.assertIsNone(subgraph)
                continue
            print(subgraph)
            self.assertEqual(node_num, len(subgraph.nodes()))
            self.assertEqual(relation_num, len(subgraph.relationships()))

            for n in subgraph.nodes():
                print(n)
            for r in subgraph.relationships():
                print(r)

            for r in subgraph.relationships():
                is_contain = self.graphClient.get_id_for_node(
                    r.start_node()) == node_id or self.graphClient.get_id_for_node(
                    r.end_node()) == node_id
                self.assertTrue(is_contain)

            is_contain = False
            for n in subgraph.nodes():
                is_contain = self.graphClient.get_id_for_node(n) == node_id
                if is_contain == True:
                    break

            self.assertTrue(is_contain)

    def test_expand_nodes_with_filter_nodes(self):
        graphClient = DefaultGraphAccessor(GraphClient())

        # test_case = [(55730, True, 50, 50), (15555, True, 4, 4), (93008, True, 10, 11), (1708, True, 8, 7)]
        test_case = [(55730, True, 50, 50), ]
        graphJsonParser = GraphJsonParser()
        for node_id, is_valid, node_num, relation_num in test_case:
            print("test case=", node_id, is_valid, node_num, relation_num)
            subgraph = graphClient.expand_node_for_adjacent_nodes_to_subgraph(node_id)
            subgraph_json = graphJsonParser.parse_subgraph_to_public_json(subgraph)
            print(subgraph_json)
            if is_valid:
                self.assertNotEqual(subgraph_json, {"nodes": [], "relations": []})
            else:
                self.assertEqual(subgraph_json, {"nodes": [], "relations": []})
                continue
            self.assertEqual(node_num, len(subgraph_json["nodes"]))
            self.assertEqual(relation_num, len(subgraph_json["relations"]))

            for n in subgraph_json["nodes"]:
                print(n)
            for r in subgraph_json["relations"]:
                print(r)
