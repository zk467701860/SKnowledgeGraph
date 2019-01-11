from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from graph_operation import GraphOperation

graphClient = DefaultGraphAccessor(GraphClient(server_number=1))


class JavaFieldTypeLinkerOperation(GraphOperation):
    name = 'JavaFieldTypeLinkerOperation'

    def operate(self, node):
        type_part_name = node["return value type"]
        if type_part_name:
            type_node = graphClient.find_one_by_alias_name_property("java class",
                                                                    type_part_name)
            if type_node is not None:
                relation = Relationship(node, "type of", type_node)
                graphClient.merge(relation)
        return node, node
