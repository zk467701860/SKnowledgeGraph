from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.operation.java_field_add_alias_property import JavaFieldAliasPropertyCreateOperation
from skgraph.graph.graph_operator import GraphOperator

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(400, ['java field'], JavaFieldAliasPropertyCreateOperation())
