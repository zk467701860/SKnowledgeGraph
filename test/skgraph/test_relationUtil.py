from unittest import TestCase

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.relation_util import RelationUtil


class TestRelationUtil(TestCase):
    def setUp(self):
        graphClient = DefaultGraphAccessor(GraphClient(server_number=1))
        relation_util = RelationUtil(graphClient)

        self.relation_util = relation_util

    def test_init_relation_description(self):
        self.relation_util.init_relation_description()
        print(self.relation_util.relation_description_map)

    def test_get_description_by_relation_type(self):
        print(self.relation_util.get_description_by_relation_type("is"))
        print(self.relation_util.get_description_by_relation_type("belong to"))

    def test_get_relation_description_json(self):
        print(self.relation_util.get_relation_description_json("is"))
        print(self.relation_util.get_relation_description_json("belong to"))

    def test_get_relation_description_json_list(self):
        print(self.relation_util.get_relation_description_json_list(["is","belong to"]))
