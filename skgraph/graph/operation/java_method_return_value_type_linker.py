from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from graph_operation import GraphOperation

graphClient = DefaultGraphAccessor(GraphClient(server_number=1))


class JavaMethodReturnValueTypeLinkerOperation(GraphOperation):
    name = 'JavaMethodReturnValueTypeLinkerOperation'

    def operate(self, node):
        type_part_name = node["return value type"]

        # remove "\xa0" in the word
        if type_part_name is not None and type_part_name is not "":
            type_part_name = "".join(type_part_name.split())
            node["return value type"] = type_part_name
        if type_part_name:
            type_node = graphClient.find_one_by_alias_name_property("java class",
                                                                    type_part_name)
            if type_node is not None:
                relation = Relationship(node, "return value type of", type_node)
                graphClient.merge(relation)
        return node, node
