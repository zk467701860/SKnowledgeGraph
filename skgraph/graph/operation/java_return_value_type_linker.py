from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from graph_operation import GraphOperation

graphClient = DefaultGraphAccessor(GraphClient(server_number=1))


class JavaReturnValueTypeLinkerOperation(GraphOperation):
    name = 'JavaReturnValueTypeLinkerOperation'

    def operate(self, node):
        return_value_type = node["value type"]
        if return_value_type:
            type_node = graphClient.find_one_by_alias_name_property("java class",
                                                                    return_value_type)
            if type_node is not None:
                relation = Relationship(node, "type of", type_node)
                graphClient.merge(relation)
        return node, node
