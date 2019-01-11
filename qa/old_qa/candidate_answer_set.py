import traceback


class CandidateAnswerSet:
    '''
    a object contain all the candidate answer and the relative node for decide the answer
    '''

    def __init__(self, important_kernel_nodes_subgraph=None, normal_condition_nodes_subgraph=None,
                 important_kernel_node_list_score_map=None, normal_condition_node_list_score_map=None,
                 key_word_path_subgraph=None, important_kernel_nodes_expand_subgraph=None,
                 normal_condition_node_expand_subgraph=None,
                 candidate_key_nodes_graph_map=None):
        self.candidate_graph=None
        if normal_condition_node_list_score_map is None:
            normal_condition_node_list_score_map = {}
        if important_kernel_node_list_score_map is None:
            important_kernel_node_list_score_map = {}
        if normal_condition_nodes_subgraph is None:
            normal_condition_nodes_subgraph = []
        if important_kernel_nodes_subgraph is None:
            important_kernel_nodes_subgraph = []
        self.important_kernel_nodes_subgraph = important_kernel_nodes_subgraph  # all the key node, Node class,from py2neo import Node
        self.normal_condition_nodes_subgraph = normal_condition_nodes_subgraph  # all the key node except the normal, Node class,from py2neo import Node

        self.important_kernel_node_list_score_map = important_kernel_node_list_score_map  # the score of one node,get by important_kernel_node_list_score_map[str(node id)]
        self.normal_condition_node_list_score_map = normal_condition_node_list_score_map

        self.key_word_path_subgraph = key_word_path_subgraph  # the subgraph which contain the path to connect the important_kernel and the normal_condition_node

        self.important_kernel_nodes_expand_subgraph = important_kernel_nodes_expand_subgraph  # the subgraph expand by the important_kernel_node
        self.normal_condition_node_expand_subgraph = normal_condition_node_expand_subgraph  # the subgraph expand by the normal_condition_node

        self.candidate_key_nodes_graph_map = candidate_key_nodes_graph_map  # store the key word and the node related tod the key word,in subgraph object,candidate_key_nodes_graph_map['java']=subgraph
        try:
            self.init_candidate_graph()
        except Exception, error:
            traceback.print_exc()

    def init_candidate_graph(self):
        self.candidate_graph = self.__merge_subgraph(self.important_kernel_nodes_subgraph,
                                                     self.normal_condition_node_expand_subgraph,
                                                     self.important_kernel_nodes_expand_subgraph,
                                                     self.key_word_path_subgraph, self.normal_condition_nodes_subgraph)

    def __merge_subgraph(self, *subgraph):
        team_list = []
        for g in subgraph:
            if g is not None and g:
                team_list.append(g)
        if team_list is not []:
            if len(team_list) == 1:
                return team_list[0]
            elif len(team_list) == 2:
                return team_list[0]|team_list[1]
            else:
                start_graph = team_list[0]
                team_list = team_list[1:]
                for g in team_list:
                    start_graph = start_graph | g
                return subgraph
        else:
            return None

    def print_to_console(self):
        print '---------------------------'
        print 'candidate_graph=', self.candidate_graph
        print 'important_kernel_nodes_subgraph=', self.important_kernel_nodes_subgraph
        print 'important_kernel_node_list_score_map=', self.important_kernel_node_list_score_map
        print 'normal_condition_nodes_subgraph=', self.normal_condition_nodes_subgraph
        print 'normal_condition_node_list_score_map=', self.normal_condition_node_list_score_map
        print 'key_word_path_subgraph=', self.key_word_path_subgraph
        print 'important_kernel_nodes_expand_subgraph=', self.important_kernel_nodes_expand_subgraph
        print 'normal_condition_node_expand_subgraph=', self.normal_condition_node_expand_subgraph
        print '---------------------------'
