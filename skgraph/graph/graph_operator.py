from py2neo import Graph

from accessor.graph_accessor import GraphAccessor, GraphClient, DefaultGraphAccessor
from shared.logger_util import Logger

_logger = Logger("GraphOperator").get_log()


class GraphOperator:
    '''
        a operator on graph,
        a wrapper class for client used Neo4j client.
        firstly,it will create the connection to graph by config json in this directory.
    '''

    def __init__(self, graph):
        '''
        init with a Graph object
        :param graph: ::GraphAccessor, ::GraphClient,::Graph
        '''
        if isinstance(graph, GraphAccessor):
            self._graph = graph.graph
        elif isinstance(graph, GraphClient):
            self._graph = graph.graph
        elif isinstance(graph, Graph):
            self._graph = graph
        else:
            self._graph = None
        self.graph_accessor = None

    def operate_on_all_nodes(self, step=5000, labels=None, *operators):
        self.graph_accessor = DefaultGraphAccessor(self._graph)
        if labels is None:
            labels = []

        if labels:
            max_id = self.graph_accessor.get_max_id_for_labels(*labels)
            min_id = self.graph_accessor.get_min_id_for_labels(*labels)
        else:
            max_id = self.graph_accessor.get_max_id_for_node()
            min_id = 0
        self.operate_on_all_nodes_in_specific_scope(min_id, max_id, step, labels, *operators)

    def operate_on_all_nodes_in_specific_scope(self, start_id, end_id, step=5000, labels=None, *operators):
        if labels is None:
            labels = []
        if labels:
            max_id = self.graph_accessor.get_max_id_for_labels(*labels)
            min_id = self.graph_accessor.get_min_id_for_labels(*labels)

            min_id = max(start_id, min_id)
            max_id = min(end_id, max_id)
        else:
            max_id = self.graph_accessor.get_max_id_for_node()
            min_id = 0
            min_id = max(start_id, min_id)
            max_id = min(end_id, max_id)

        iteration = range(min_id, max_id, step)
        for start_id in iteration:
            try:
                end_id = min(start_id + step, max_id)
                update_graph = self.operate_in_scope(start_id, end_id, labels, *operators)
                _logger.info("start id=%s,end_id=%s", str(start_id), str(end_id))
                if update_graph is not None:
                    _logger.info("update graph successfully")
                else:
                    _logger.info("update graph is None")
            except Exception, error:
                _logger.exception("")

    def operate_in_scope(self, start_id, end_id, labels, *operators):
        if labels is not []:
            node_list = self.graph_accessor.get_node_in_scope_with_labels(start_id, end_id, *labels)
        else:
            node_list = self.graph_accessor.get_node_in_scope(start_id=start_id, end_id=end_id)

        result_subgraph = None
        for node in node_list:
            current_node = node
            for operator in operators:
                current_node, related_graph = operator.operate(current_node)
                if result_subgraph is not None:
                    self.graph_accessor.push(related_graph)
                    self.graph_accessor.merge(related_graph)
        return result_subgraph
