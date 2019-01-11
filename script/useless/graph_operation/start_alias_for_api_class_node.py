from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.operation.java_class_add_alias_property import JavaClassAliasPropertyCreateOperation
from skgraph.graph.graph_operator import GraphOperator

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(1000, ['java class'], JavaClassAliasPropertyCreateOperation())
