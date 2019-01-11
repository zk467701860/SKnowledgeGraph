from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from graph_operation import GraphOperation

graphClient = DefaultGraphAccessor(GraphClient(server_number=1))


class JavaClassParentClassLinkerOperation(GraphOperation):
    name = 'JavaClassParentClassLinkerOperation'

    def operate(self, node):
        parent_class = node["parent class"]
        if parent_class and parent_class != "null":
            type_node = graphClient.find_one_by_name_property(
                label="java class",
                name=parent_class)
            if type_node is not None:
                relation = Relationship(node, "extends", type_node)
                graphClient.merge(relation)
        return node, node
