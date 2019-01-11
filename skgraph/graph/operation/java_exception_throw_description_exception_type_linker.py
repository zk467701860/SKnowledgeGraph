from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from graph_operation import GraphOperation

graphClient = DefaultGraphAccessor(GraphClient(server_number=1))


class JavaThrowExceptionDescriptionTypeLinkerOperation(GraphOperation):
    name = 'JavaThrowExceptionDescriptionTypeLinkerOperation'

    def operate(self, node):
        exception_part_name = node["exception type"]
        if exception_part_name:
            type_node = graphClient.find_one_by_alias_name_property("java class",
                                                                    exception_part_name)
            if type_node is not None:
                relation = Relationship(node, "exception type", type_node)
                graphClient.merge(relation)
        return node, node
