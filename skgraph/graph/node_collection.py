from py2neo import Graph

from skgraph.graph.accessor.graph_accessor import GraphAccessor, GraphClient, DefaultGraphAccessor
from shared.logger_util import Logger

_logger = Logger("NodeCollection").get_log()


class NodeCollection:

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

    def get_all_nodes(self, step=5000, labels=None):
        total_node_list = []
        self.graph_accessor = DefaultGraphAccessor(self._graph)
        if labels is None:
            labels = []

        if labels:
            max_id = self.graph_accessor.get_max_id_for_labels(*labels)
            min_id = self.graph_accessor.get_min_id_for_labels(*labels)
        else:
            max_id = self.graph_accessor.get_max_id_for_node()
            min_id = 0

        iteration = range(min_id, max_id, step)
        for start_id in iteration:
            try:
                end_id = min(start_id + step, max_id)
                nodes_in_scope = self.get_nodes_in_scope(start_id, end_id, labels)
                _logger.info("start id=%s,end_id=%s", str(start_id), str(end_id))
                if nodes_in_scope is not None:
                    _logger.info("get nodes in scope successfully")
                    total_node_list.extend(nodes_in_scope)
                else:
                    _logger.info("get nodes in scope failed")
            except Exception, error:
                _logger.exception("")
        return total_node_list

    def get_nodes_in_scope(self, start_id, end_id, labels):
        if labels is not []:
            node_list = self.graph_accessor.get_node_in_scope_with_labels(start_id, end_id, *labels)
        else:
            node_list = self.graph_accessor.get_node_in_scope(start_id=start_id, end_id=end_id)
        return node_list