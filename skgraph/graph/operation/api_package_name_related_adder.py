from py2neo import Relationship

from skgraph.graph.accessor.factory import NodeBuilder
from graph_operation import GraphOperation


class APIPackageNameRelatedOperation(GraphOperation):
    name = 'APIPackageNameRelatedOperation'

    def operate(self, node):
        if node['name']:
            graph_updated = node
            package_name_list = node['name'].split(".")
            if len(package_name_list) >= 2:
                for key_word_name in package_name_list:
                    node, team_subgraph = self.build_package_name_relation(key_word_name, node)
                    graph_updated = graph_updated | team_subgraph
                return node, graph_updated

        return node, node

    def build_package_name_relation(self, concept_name, node):
        end_node = NodeBuilder().add_label("api concept").add_label_concept().add_one_property(property_name='name',
                                                                      property_value=concept_name).build()
        relation = Relationship(node, 'package name related', end_node)
        return node, node | relation | end_node
