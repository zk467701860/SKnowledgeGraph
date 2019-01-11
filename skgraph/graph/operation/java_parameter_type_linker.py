from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from graph_operation import GraphOperation

graphClient = DefaultGraphAccessor(GraphClient(server_number=1))


class JavaParameterTypeLinkerOperation(GraphOperation):
    name = 'JavaParameterTypeLinkerOperation'

    def operate(self, node):
        parameter_full_type_name = node["formal parameter type full name"]
        if parameter_full_type_name:
            type_node = graphClient.find_one_by_name_property("api", parameter_full_type_name)
            if type_node is not None:
                relation = Relationship(node, "type of", type_node)
                graphClient.merge(relation)
        return node, node
