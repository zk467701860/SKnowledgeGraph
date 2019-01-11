from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.graph_operator import GraphOperator
from skgraph.graph.operation.java_exception_throw_description_exception_type_linker import \
    JavaThrowExceptionDescriptionTypeLinkerOperation

graphOperator = GraphOperator(GraphClient(server_number=1))
graphOperator.operate_on_all_nodes(500, ['java throw exception description'],
                                   JavaThrowExceptionDescriptionTypeLinkerOperation())
