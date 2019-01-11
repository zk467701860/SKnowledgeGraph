import math

from answer import Answer
from answer_set import AnswerSet
from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient


class AnswerGenerator:
    stackoverflow_word2vec_model = None
    # path = 'E:\Research\word2vec\model\so_word_embedding_model'
    # path = 'model/so_word_embedding_model'

    def __init__(self):
        #file_dir = os.path.split(os.path.realpath(__file__))[0]
        #self.path = os.path.join(file_dir, self.path)
        #self.stackoverflow_word2vec_model = Word2Vec.load(self.path)
        self.graph_operator = DefaultGraphAccessor(GraphClient())
        print "done load word2vec"

    def generate_answer_set(self, question, candidate_answer_set):
        '''
        generate the answer set from candidate_answer_set for one question,
        the answer set may container some answer,but the answer ranked by the possibility to be right answer
        the first answer is the most likely answer
        :param question: question object
        :param candidate_answer_set: candidate answer set
        :return: the answer set contain a set of answers
        '''
        # todo complete this answer generator
        answer_list = []

        id_node_dict = self.id_node_dict(candidate_answer_set)
        id_relation_dict = self.id_relation_dict(candidate_answer_set)
        print question.get_keywords()
        #print self.print_data(candidate_answer_set)
        question_keywords = question.get_keywords()
        keywords = []
        for each in question_keywords:
            each = each.lower()
            if each.strip().find(" ") != -1:
                keywords.extend(each.split())
            else:
                keywords.append(each)
        print keywords
        question_vec = self.generate_question_vector(keywords)
        nodes_from_relation = self.relation_similarity(candidate_answer_set, keywords, question_vec, id_relation_dict)
        nodes_result_vecs = self.generate_candidate_vectors(nodes_from_relation)
        nodes_result = {key: self.question_answer_similarity(question_vec, nodes_result_vecs.get(key)) for key in nodes_result_vecs.keys()}
        result, others = self.simple_match(keywords, candidate_answer_set.candidate_graph.nodes())

        match_result_vecs = self.generate_candidate_vectors(result)
        match_result = {key: self.question_answer_similarity(question_vec, match_result_vecs.get(key)) for key in
                        match_result_vecs.keys()}
        others_vecs = self.generate_candidate_vectors(others)
        similar_result = {key: self.question_answer_similarity(question_vec, others_vecs.get(key)) * 0.8 for key in
                          others_vecs.keys()}
        '''print similar_result
        sorted_similar_result = self.result_sort(similar_result)
        sorted_match_result = self.result_sort(match_result)
        print sorted_similar_result
        print sorted_match_result
        sorted_result = sorted_match_result + sorted_similar_result
        print sorted_result
        sorted_result = self.list_sort(sorted_result)
        print sorted_result'''
        full_result = dict(nodes_result.items() + match_result.items() + similar_result.items())
        sorted_result = self.result_sort(full_result)
        print sorted_result

        property_sililar_result = self.property_sililarity(sorted_result, id_node_dict, question_vec)
        sorted_property_result = self.result_sort(property_sililar_result)
        print sorted_property_result

        for i in range(0, 5):
            (id, score) = sorted_result[i]
            node = id_node_dict.get(id)
            node_list = []
            node_list.append(node)
            answer_text = self.get_entity_name(node)
            answer = Answer(answer_text, node_list, score)
            answer_list.append(answer)

        return AnswerSet(answer_list=answer_list)

    def property_sililarity(self, sorted_result, id_node_dict, question_vec):
        result = {}
        for i in range(0, 10):
            (id, score) = sorted_result[i]
            node = id_node_dict.get(id)
            properties = dict(node)
            cos_similarity = 0
            for key in properties:
                key_lists = self.extract_names(key)
                each_cos_similarity = 0
                for each in key_lists:
                    try:
                        vec = [value for value in self.stackoverflow_word2vec_model.wv[each]]
                        each_cos_similarity += self.question_answer_similarity(question_vec, vec)
                    except KeyError as ke:
                        print KeyError, ":", str(ke)
                cos_similarity += (each_cos_similarity / len(key_lists))
            property_score = score * cos_similarity
            result.setdefault(id, property_score)
        return result

    def calculate_cosine_similarity(self, vec1, vec2):
        if not len(vec1) == len(vec2):
            return 0
        if vec1 == [0 for i in range(0, len(vec1))] or vec2 == [0 for i in range(0, len(vec2))]:
            return 0
        numerator = sum([vec1[i] * vec2[i] for i in range(0, len(vec1))])
        vec1_dis = math.sqrt(sum([vec1[i] * vec1[i] for i in range(0, len(vec1))]))
        vec2_dis = math.sqrt(sum([vec2[i] * vec2[i] for i in range(0, len(vec2))]))
        cos_sim = numerator / (vec1_dis * vec2_dis)
        return cos_sim

    def question_answer_similarity(self, question_vecs, answer_vec):
        similarity = 0
        for each_keyword in question_vecs:
            keyword_vec = question_vecs[each_keyword]
            similarity += self.calculate_cosine_similarity(keyword_vec, answer_vec)
        return similarity / len(question_vecs)

    def generate_question_vector(self, question_keywords):
        vec = [0 for i in range(0, 400)]
        question_word_vecs = {}
        for word in question_keywords:
            try:
                vec = [value for value in self.stackoverflow_word2vec_model.wv[word]]
                # question_vec = [(a + b) for a, b in zip(question_vec, vec)]
            except KeyError as ke:
                print KeyError, ":", str(ke)
            question_word_vecs.setdefault(word, vec)
        return question_word_vecs

    def generate_candidate_vectors(self, others):
        candidate_answer_vecs = {}
        for node in others:
            node_id = self.graph_operator.get_id_for_node(node)
            name = self.get_entity_name(node)
            name_list = name.split()
            name_vec = [0 for i in range(0, 400)]
            for name in name_list:
                try:
                    temp_vec = self.stackoverflow_word2vec_model.wv[name]
                    # print temp_vec
                    name_vec = [a + b for a, b in zip(name_vec, temp_vec)]
                except KeyError as ke:
                    print KeyError, ":", str(ke)
            candidate_answer_vecs.setdefault(node_id, name_vec)
        return candidate_answer_vecs

    def relation_similarity(self, candidate_answer_set, keywords, question_vec, id_relation_dict):
        node_result = []
        relation_id_score = {}
        for relation in candidate_answer_set.candidate_graph.relationships():
            if self.relation_simple_match(relation, keywords):
                node_result.append(relation.start_node())
                node_result.append(relation.end_node())
            else:
                relation_id = self.graph_operator.get_id_for_node(relation)
                score = self.relation_cos_similarity(relation, question_vec)
                relation_id_score.setdefault(relation_id, score)
        sorted_relation_id_score = self.result_sort(relation_id_score)
        for i in range(0, 3):
            id, score = sorted_relation_id_score[i]
            relation = id_relation_dict.get(id)
            node_result.append(relation.start_node())
            node_result.append(relation.end_node())
        return node_result

    def get_node_by_id(self, node_id_list, id_node_dict):
        result = []
        for each_id in node_id_list:
            node = id_node_dict.get(each_id)
            result.append(node)
        return result


    def relation_simple_match(self, relation, question_keywords):
        relation_names = self.extract_names(relation.type())
        for each_name in relation_names:
            if each_name != '' and each_name.lower() in question_keywords:
                return True
        return False

    def relation_cos_similarity(self, relation, question_vec):
        relation_names = self.extract_names(relation.type())
        each_cos_similarity = 0
        for each_name in relation_names:
            try:
                vec = [value for value in self.stackoverflow_word2vec_model.wv[each_name]]
                each_cos_similarity += self.question_answer_similarity(question_vec, vec)
            except KeyError as ke:
                print KeyError, ":", str(ke)
        return each_cos_similarity / len(relation_names)

    def simple_match(self, question_keywords, node_list):
        result = []
        for node in node_list:
            name = self.get_entity_name(node)
            temp_name = name.lower()
            print name
            if temp_name != '' and temp_name in question_keywords:
                result.append(node)
        candidate_set = set(node_list)
        result_set = set(result)
        other_set = candidate_set - result_set
        others = list(other_set)
        '''print "result nodes: "
        for node in result:
            name = self.get_entity_name(node)
            print name'''
        return result, others

    def result_sort(self, result_dict):
        return sorted(result_dict.iteritems(), key=lambda asd: asd[1], reverse=True)

    def list_sort(self, result_list):
        return sorted(result_list, key=lambda asd: asd[1], reverse=True)

    def get_entity_name(self, node):
        if node.has_key('name'):
            name = node.get('name')
        elif node.has_key('labels_en'):
            name = node.get('labels_en')
        else:
            name = ''
        return name

    def extract_names(self, name):
        result = []
        if name.find("_") != -1:
            result.extend(name.split("_"))
        elif name.find(" ") != -1:
            result.extend(name.split(" "))
        else:
            result.append(name)
        return result

    def id_node_dict(self, candidate_answer_set):
        result = {}
        for node in candidate_answer_set.candidate_graph.nodes():
            id = self.graph_operator.get_id_for_node(node)
            result.setdefault(id, node)
        return result

    def id_relation_dict(self, candidate_answer_set):
        result = {}
        for relation in candidate_answer_set.candidate_graph.relationships():
            id = self.graph_operator.get_id_for_node(relation)
            result.setdefault(id, relation)
        return result

    def print_data(self, candidate_answer_set):
        print "candidate_graph data:"
        for node in candidate_answer_set.candidate_graph.nodes():
            name = self.get_entity_name(node)
            print name

        print "important_kernel_nodes_subgraph data:"
        for node in candidate_answer_set.important_kernel_nodes_subgraph.nodes():
            name = self.get_entity_name(node)
            print name

        print "normal_condition_nodes_subgraph data:"
        for node in candidate_answer_set.normal_condition_nodes_subgraph.nodes():
            name = self.get_entity_name(node)
            print name

        print "key_word_path_subgraph data:"
        for node in candidate_answer_set.key_word_path_subgraph.nodes():
            name = self.get_entity_name(node)
            print name

        print "important_kernel_nodes_expand_subgraph data:"
        for node in candidate_answer_set.important_kernel_nodes_expand_subgraph.nodes():
            name = self.get_entity_name(node)
            print name

        print "normal_condition_node_expand_subgraph data:"
        for node in candidate_answer_set.normal_condition_node_expand_subgraph.nodes():
            name = self.get_entity_name(node)
            print name
