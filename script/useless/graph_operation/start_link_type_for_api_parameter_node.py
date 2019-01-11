from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.operation.java_parameter_type_linker import JavaParameterTypeLinkerOperation
from skgraph.graph.graph_operator import GraphOperator

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(500, ['java method parameter'], JavaParameterTypeLinkerOperation())
