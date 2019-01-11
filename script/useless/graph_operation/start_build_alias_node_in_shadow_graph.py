from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.graph_operator import GraphOperator
from skgraph.graph.operation.build_node_alias_node_graph import BuildAliasNodeShadowGraphOperation

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(1000, ['relation'], BuildAliasNodeShadowGraphOperation())
graphOperator.operate_on_all_nodes(1000, ['entity'], BuildAliasNodeShadowGraphOperation())
