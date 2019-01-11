from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.graph_operator import GraphOperator
from skgraph.graph.operation.wall_node_fix import FixWallNodeLabelErrorOperation

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(3000, ['wall'], FixWallNodeLabelErrorOperation())
