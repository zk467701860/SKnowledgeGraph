from unittest import TestCase

from model_util.graph_vector import GraphNode2Vec, NodeSimilarty


class TestQAByNode(TestCase):
    def test_qe_similarity(self):
        output_path = './knowledge_construction/graph_vector/emb/output.emb'
        n = GraphNode2Vec()
        print(n.graph)
        relation_list, type_list = n.getAllRelationship()
        model = n.trainEdgeList(relation_list, output_path)
        n.getNodeVec(model)
        test = NodeSimilarty()
        test.load_model()
        cos = test.get_similarty_between(30, 518)
        print(cos)
