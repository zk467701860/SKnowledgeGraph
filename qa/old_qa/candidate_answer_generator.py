from candidate_answer_set import CandidateAnswerSet
from skgraph.graph.accessor.graph_accessor import GraphClient
from qustion_template import WhatIsQuestionTemplate, QuestionTemplate
from skgraph.graph.accessor.graph_client_for_qustion_answer import QuestionAndAnswerGraphAccessor


class CandidateAnswerSetGenerator:
    top_num_for_name_search = 20
    KERNEL_NODE_NUMBER_TO_GET_PATH = 10
    NORMAL_CONDITION_NODE_NUMBER_TO_EXPAND = 5

    def __init__(self):
        self.graphClient = QuestionAndAnswerGraphAccessor(GraphClient())

    def generate_question_template(self, question):
        '''
        generate the question template match the question
        :param question: the question object
        :return: the question template
        '''
        question_template = None
        if question.query.query_type == QuestionTemplate.WHAT_IS_LIKE_QUESTION:
            if question.NP and len(question.NP) > 0:
                question_template = WhatIsQuestionTemplate(start_entity_name=question.NP[0])

        return question_template

    def generate_candidate_answer_set(self, question):
        candidate_answer_set = None

        candidate_answer_set = self.generate_candidate_answer_set_from_question_template(question)
        if candidate_answer_set is None:
            return self.generate_candidate_answer_set_in_general_way(question)
        else:
            return candidate_answer_set

    def generate_candidate_answer_set_from_question_template(self, question):
        question_template = self.generate_question_template(question)
        if question_template:
            if question_template.template_type == QuestionTemplate.WHAT_IS_LIKE_QUESTION:
                return self.generate_candidate_answer_set_for_WhatIsXXX(question, question_template)

            return None
        else:
            return None

    def generate_candidate_answer_set_for_WhatIsXXX(self, question, question_template):

        entity_subgraph, score_map = self.graphClient.entity_linking_for_name(question_template.start_entity_name,
                                                                              top_number=5)
        if entity_subgraph is not None:
            what_is_relation_subgraph = self.graphClient.get_what_is_relation_for_subgraph_in_subgraph(entity_subgraph)
            return CandidateAnswerSet(important_kernel_nodes_subgraph=entity_subgraph,
                                      important_kernel_node_list_score_map=score_map,
                                      important_kernel_nodes_expand_subgraph=what_is_relation_subgraph)
        else:
            return None

    def generate_candidate_answer_set_for_query_type1(self, question):
        '''
        generate candidate answer for the following
        answer_set = system.full_answer(question_text='what class can perform data collection in java?')
        answer_set = system.full_answer(question_text='What api can achieve file read and write function?')
        answer_set = system.full_answer(question_text="I want to know what class can perform data collection in java")

        :param question:
        :return:
        '''

    def generate_candidate_answer_set_in_general_way(self, question):
        '''
        generate the candidate answer set for question,in a general way
        :param question: the question object
        :return: candidate_answer_set
        '''
        candidate_keyword_to_subgraph_map = {}

        for keyword in question.NP:
            candidate_sugraph_to_keyword = self.search_subgraph_by_name_without_alias_node(keyword,
                                                                                           CandidateAnswerSetGenerator.top_num_for_name_search)
            if candidate_sugraph_to_keyword is not None:
                candidate_keyword_to_subgraph_map[keyword] = candidate_sugraph_to_keyword
        candidate_functions_related_key_nodes_subgraph = None
        if len(question.Func) > 0:
            function_description = question.Func[0]
            candidate_functions_related_key_nodes_subgraph, score_map = self.graphClient.search_api_by_function_description_with_weight(
                function_description, top_number=20)

        key_word_answer_path_subgraph = None
        other_condition_graph_list = []
        kernel_nodes_graph = None
        if candidate_functions_related_key_nodes_subgraph is not None:
            kernel_nodes_graph = candidate_functions_related_key_nodes_subgraph
            other_condition_graph_list = candidate_keyword_to_subgraph_map.values()
        else:
            all_condidate_nodes_list = candidate_keyword_to_subgraph_map.values()
            if len(all_condidate_nodes_list) >= 1:
                kernel_nodes_graph = all_condidate_nodes_list[0]
                if len(all_condidate_nodes_list) >= 2:
                    other_condition_graph_list = all_condidate_nodes_list[1:]

        if kernel_nodes_graph is None:
            subgraph = self.generate_candidate_nodes_by_name(question_text=question.question_text, top_num=50)
            if subgraph:
                return CandidateAnswerSet(important_kernel_nodes_subgraph=subgraph.nodes())
            else:
                return CandidateAnswerSet()
        team_kernel_nodes = self.get_sub_of_list(kernel_nodes_graph.nodes(),
                                                 CandidateAnswerSetGenerator.KERNEL_NODE_NUMBER_TO_GET_PATH)
        for other_condition_subgraph in other_condition_graph_list:
            other_condition_subgraph = self.get_sub_of_list(other_condition_subgraph.nodes(),
                                                            CandidateAnswerSetGenerator.NORMAL_CONDITION_NODE_NUMBER_TO_EXPAND)
            shortest_path_subgraph = self.graphClient.get_shortest_path_in_two_node_set_in_subgraph(team_kernel_nodes,
                                                                                                    other_condition_subgraph)
            if key_word_answer_path_subgraph is None:
                key_word_answer_path_subgraph = shortest_path_subgraph
            else:
                key_word_answer_path_subgraph = key_word_answer_path_subgraph | shortest_path_subgraph

        normal_condition_node_expand_subgraph = None
        important_kernel_nodes_expand_subgraph = self.graphClient.expand_node_for_directly_adjacent_nodes_to_subgraph_for_all_nodes(
            kernel_nodes_graph, limit=30)
        normal_condition_nodes_subgraph = self.merge_subgraph_list_to_subgraph(other_condition_graph_list)
        if normal_condition_nodes_subgraph is not None:
            normal_condition_node_expand_subgraph = self.graphClient.expand_node_for_directly_adjacent_nodes_to_subgraph_for_all_nodes(
                subgraph=normal_condition_nodes_subgraph, limit=100)

        return CandidateAnswerSet(important_kernel_nodes_subgraph=kernel_nodes_graph,
                                  normal_condition_nodes_subgraph=normal_condition_nodes_subgraph,
                                  key_word_path_subgraph=key_word_answer_path_subgraph,
                                  important_kernel_nodes_expand_subgraph=important_kernel_nodes_expand_subgraph,
                                  normal_condition_node_expand_subgraph=normal_condition_node_expand_subgraph,
                                  candidate_key_nodes_graph_map=candidate_keyword_to_subgraph_map)

    def get_sub_of_list(self, data_set, number):
        if len(data_set) <= number:
            return data_set
        else:
            return list(data_set)[:number]

    def generate_candidate_nodes_by_name(self, question_text, top_num=20):
        subgraph = self.search_subgraph_by_name_without_alias_node(question_text, top_num)
        subgraph = self.graphClient.expand_node_for_directly_adjacent_nodes_to_subgraph_for_all_nodes(subgraph=subgraph)
        return subgraph

    def merge_subgraph_list_to_subgraph(self, subgraph_list):
        result_subgraph = None
        for subgraph in subgraph_list:
            if result_subgraph:
                result_subgraph = result_subgraph | subgraph
            else:
                result_subgraph = subgraph
        return result_subgraph
