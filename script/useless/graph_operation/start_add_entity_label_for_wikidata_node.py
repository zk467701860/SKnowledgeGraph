from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.graph_operator import GraphOperator
from skgraph.graph.operation.api_node_entity_label_adder import APINodeEntityLabelAdderOperation

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(500, ['wikidata'], APINodeEntityLabelAdderOperation())
