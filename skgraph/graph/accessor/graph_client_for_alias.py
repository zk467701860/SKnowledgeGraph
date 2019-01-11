from py2neo import Relationship

from factory import NodeBuilder
from graph_accessor import GraphAccessor
from shared.logger_util import Logger

_logger = Logger("AliasGraphAccessor").get_log()


class AliasGraphAccessor(GraphAccessor):
    def find_root_entity_by_alias_name(self, alias):
        query = "match (n:alias)-[:alias]-(m) where n.name='{alias}' return  m"
        query =  query.format(alias=alias)
        return self.graph.run(query)

    def build_alias_relation(self, alias, node):
        end_node = self.find_or_create_alias_node(alias)
        relation = Relationship(node, 'alias', end_node)
        self.graph.merge(relation)

    def find_or_create_alias_node(self, alias):
        end_node = NodeBuilder().add_as_alias().add_one_property(property_name='name',
                                                                 property_value=alias).build()
        self.graph.merge(end_node)
        return end_node

    def create_alias_node_for_name(self, name, node_id):
        alias_node = NodeBuilder().add_as_alias().add_one_property("name", name).build()
        self.graph.merge(alias_node)
        alias_node_link_id_list = alias_node["link_id"]
        if alias_node_link_id_list is None or alias_node_link_id_list is []:
            alias_node["link_id"] = [node_id]
        else:
            s = set(alias_node_link_id_list)
            s.add(node_id)
            alias_node["link_id"] = list(s)
        self.graph.push(alias_node)
