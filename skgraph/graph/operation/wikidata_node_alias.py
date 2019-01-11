from py2neo import Relationship

from skgraph.graph.accessor.factory import NodeBuilder
from graph_operation import GraphOperation


class AddAliasOperationForWikidataNode(GraphOperation):
    name = 'AddAliasOperationForWikidataNode'

    def operate(self, node):
        if node['aliases_en']:
            if type(node['aliases_en']) == list:
                for alias in node['aliases_en']:
                    # print "list alias=", alias
                    return self.build_alias_relation(alias, node)
            else:
                if ",," in node['aliases_en']:
                    aliases = node['aliases_en'].split(",,")
                    subgraph = node
                    for alias in aliases:
                        # print "split alias=", alias
                        new_node, team = self.build_alias_relation(alias, node)
                        subgraph = subgraph | team
                    return node, subgraph
                else:
                    # print "whole str alias=", node['aliases_en']
                    return self.build_alias_relation(node['aliases_en'], node)

        return node, node

    def build_alias_relation(self, alias, node):
        end_node = NodeBuilder().add_as_alias().add_one_property(property_name='name',
                                                                 property_value=alias).build()
        relation = Relationship(node, 'alias', end_node, language='en')
        return node, node | relation | end_node
