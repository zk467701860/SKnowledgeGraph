from skgraph.graph_util.question_answer_system.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from py2neo import Relationship

from skgraph.graph.accessor.factory import NodeBuilder
from graph_operation import GraphOperation

startGraphClient = DefaultGraphAccessor(GraphClient(server_number=1))
endGraphClient = DefaultGraphAccessor(GraphClient(server_number=3)).graph


class BuildAliasNodeShadowGraphOperation(GraphOperation):
    name = 'BuildAliasNodeShadowGraphOperation'

    @staticmethod
    def init_node_builder(node):
        node_builder = NodeBuilder().add_as_alias()
        if node.has_label("api"):
            node_builder = node_builder.add_label("api")
        if node.has_label("java class"):
            node_builder = node_builder.add_label("java class")
        if node.has_label("java method"):
            node_builder = node_builder.add_label("java method")
        if node.has_label("java package"):
            node_builder = node_builder.add_label("java package")
        return node_builder

    def operate(self, node):
        name = node["name"]

        node_id = startGraphClient.get_id_for_node(node)

        if name == "" or name is None:
            return node, None
        alias_node_list = []
        transaction = endGraphClient.begin()
        start_alias_node = self.create_alias_node_by_for_node_from_other_graph(transaction, name, node)
        alias_node_list.append(start_alias_node)
        alias_name_list = node["alias"]
        if alias_name_list and type(alias_name_list) == list:
            for alias_name in alias_name_list:
                other_alias_node = BuildAliasNodeShadowGraphOperation.create_alias_node_by_for_node_from_other_graph(
                    transaction, alias_name, node)
                transaction.merge(Relationship(start_alias_node, "alias", other_alias_node))
                alias_node_list.append(other_alias_node)

        alias_name_list = node["aliases_en"]
        if alias_name_list and type(alias_name_list) == list:
            for alias_name in alias_name_list:
                other_alias_node = BuildAliasNodeShadowGraphOperation.create_alias_node_by_for_node_from_other_graph(
                    transaction, alias_name, node)
                transaction.merge(Relationship(start_alias_node, "alias", other_alias_node))
                alias_node_list.append(other_alias_node)
        transaction.commit()
        for alias_node in alias_node_list:
            BuildAliasNodeShadowGraphOperation.add_link_id_for_alias_node(alias_node, node_id, endGraphClient)
        return node, None

    @staticmethod
    def create_alias_node_by_for_node_from_other_graph(transaction, name, node):
        alias_node = BuildAliasNodeShadowGraphOperation.init_node_builder(node).add_one_property("name",
                                                                                                 name).build()
        transaction.merge(alias_node)
        return alias_node

    @staticmethod
    def add_link_id_for_alias_node(alias_node, node_id, graph):
        alias_node_link_id_list = alias_node["link_id"]
        if alias_node_link_id_list is None or alias_node_link_id_list is []:
            alias_node["link_id"] = [node_id]
        else:
            s = set(alias_node_link_id_list)
            s.add(node_id)
            alias_node["link_id"] = list(s)
        graph.push(alias_node)
