from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.graph_operator import GraphOperator
from skgraph.graph.operation.java_package_add_alias_property import JavaPackageAliasPropertyCreateOperation

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(1000, ['java package'], JavaPackageAliasPropertyCreateOperation())
