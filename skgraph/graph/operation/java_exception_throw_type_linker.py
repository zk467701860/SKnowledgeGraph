from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from graph_operation import GraphOperation

graphClient = DefaultGraphAccessor(GraphClient(server_number=1))


class JavaExceptionTypeLinkerOperation(GraphOperation):
    name = 'JavaExceptionTypeLinkerOperation'

    def operate(self, node):
        exception_part_name_list = node["throw exception"]
        if exception_part_name_list:
            for exception_part_name in exception_part_name_list:
                type_node = graphClient.find_one_by_alias_name_property(
                    label="java class",
                    name=exception_part_name)
                if type_node is not None:
                    relation = Relationship(node, "throw exception", type_node)
                    graphClient.merge(relation)
        return node, node
