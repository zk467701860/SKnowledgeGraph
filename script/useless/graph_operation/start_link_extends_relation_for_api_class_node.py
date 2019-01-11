from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.graph_operator import GraphOperator
from skgraph.graph.operation.java_class_parent_class_linker import JavaClassParentClassLinkerOperation

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(1000, ['java class'], JavaClassParentClassLinkerOperation())
