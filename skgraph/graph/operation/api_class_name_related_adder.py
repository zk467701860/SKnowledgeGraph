import re

from py2neo import Relationship

from skgraph.graph.accessor.factory import NodeBuilder
from graph_operation import GraphOperation


class APIClassNameRelatedOperation(GraphOperation):
    name = 'APIClassNameRelatedOperation'
    pattern = re.compile(r"[A-Z][a-z]+|[A-Z]+(?=[A-Z])")

    def __init__(self, graph_client):
        GraphOperation.__init__(self)
        self.graph_client = graph_client

    def operate(self, node):
        if node['name']:
            graph_updated = node
            name_list = self.get_class_seperated_list_by_java_class_name_convention(node['name'])

            if len(name_list) >= 2:
                last_name = name_list[-1]
                name_list = name_list[:-1]
                for key_word_name in name_list:
                    node, node = self.build_class_name_relation(key_word_name, node)
                node, node = self.build_last_word_name_relation(last_name, node)
                return node, node
            else:
                if len(name_list) == 1:
                    return self.build_last_word_name_relation(name_list[0], node)
        return node, node

    def build_class_name_relation(self, concept_name, node):
        end_node = NodeBuilder().add_label("api concept").add_one_property(property_name='name',
                                                                           property_value=concept_name).build()
        self.graph_client.merge(end_node)
        relation = Relationship(node, 'class name related', end_node)
        self.graph_client.merge(relation)
        return node, node

    def build_last_word_name_relation(self, concept_name, node):
        end_node = NodeBuilder().add_label("api concept").add_label_concept().add_one_property(property_name='name',
                                                                                               property_value=concept_name).build()
        self.graph_client.merge(end_node)
        name_related_relation = Relationship(node, 'class name related', end_node)
        implementation_relation = Relationship(node, 'a implementation of', end_node)

        self.graph_client.merge(name_related_relation)
        self.graph_client.merge(implementation_relation)

        return node, node

    def get_class_seperated_list_by_java_class_name_convention(self, name):
        name_list = re.findall(self.pattern, name)
        return name_list
