# -*- coding:utf8 -*-

import time

from answer import Answer
from answer_set import AnswerSet
from candidate_answer_generator import CandidateAnswerSetGenerator
from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from question_analyzer import QuestionAnalyzer
from question_preprossor import QuestionPreprossor


## todo: fix this system to answer question based on template

class OldQuestionAnswerSystem:
    def __init__(self):
        self.question_preprossor = QuestionPreprossor()
        self.question_analyzer = QuestionAnalyzer()
        self.candidate_answer_generator = CandidateAnswerSetGenerator()
        # self.answer_generator = AnswerGenerator()
        self.answer_generator = None
        self.client = DefaultGraphAccessor(GraphClient())

    def simple_answer(self, question_text):
        '''
        get a simple answer string
        :param question_text: question text
        :return: a simple answer string
        '''
        # todo complete this answer method
        return "I can't answer this question"

    def full_answer(self, question_text, top_number=10):
        '''
        get a full answer set for the question
        :param question_text: question text
        :return:  a full answer set
        '''
        question = self.question_preprossor.preprosse_question(question_text=question_text)
        question = self.question_analyzer.analyze_question(question=question)
        question.print_to_console()
        candidate_answer_set = self.candidate_answer_generator.generate_candidate_answer_set(question=question)
        answer_set = self.answer_generator.generate_answer_set(question=question,
                                                               candidate_answer_set=candidate_answer_set)
        return answer_set

    def fake_full_answer(self, question_text, top_number=10):
        '''
        get a full answer set for the question
        :param question_text: question text
        :return:  a full answer set
        '''
        ## todo fix this fake ful answer
        answer_set = AnswerSet(answer_list=[])
        return answer_set

        answer_list = []
        if 'what is java' in question_text.lower():
            node = self.client.find_node_by_id(678253)
            answer = Answer(self.get_entity_name(node), [node], 0.9)
            answer_list.append(answer)
            node = self.client.find_node_by_id(676793)
            answer = Answer(self.get_entity_name(node), [node], 0.7)
            answer_list.append(answer)
            node = self.client.find_node_by_id(7686)
            answer = Answer(self.get_entity_name(node), [node], 0.6)
            answer_list.append(answer)
            node = self.client.find_node_by_id(19204)
            answer = Answer(self.get_entity_name(node), [node], 0.4)
            answer_list.append(answer)
            node = self.client.find_node_by_id(821488)
            answer = Answer(self.get_entity_name(node), [node], 0.2)
            answer_list.append(answer)
            time.sleep(4)
        elif 'which library can process json' in question_text.lower():
            node = self.client.find_node_by_id(1518)
            answer = Answer(self.get_entity_name(node), [node], 0.8)
            answer_list.append(answer)
            node = self.client.find_node_by_id(698753)
            answer = Answer(self.get_entity_name(node), [node], 0.7)
            answer_list.append(answer)
            node = self.client.find_node_by_id(699419)
            answer = Answer(self.get_entity_name(node), [node], 0.6)
            answer_list.append(answer)
            node = self.client.find_node_by_id(700229)
            answer = Answer(self.get_entity_name(node), [node], 0.5)
            answer_list.append(answer)
            time.sleep(5)
        elif 'what string building api is thread safe' in question_text.lower():
            node = self.client.find_node_by_id(659611)
            answer = Answer(self.get_entity_name(node), [node], 0.8)
            answer_list.append(answer)
            node = self.client.find_node_by_id(52741)
            answer = Answer(self.get_entity_name(node), [node], 0.6)
            answer_list.append(answer)
            node = self.client.find_node_by_id(659612)
            answer = Answer(self.get_entity_name(node), [node], 0.1)
            answer_list.append(answer)
            time.sleep(7)
        elif 'where can i find apache' in question_text.lower():
            node = self.client.find_node_by_id(692324)
            answer = Answer(self.get_entity_name(node), [node], 0.8)
            answer_list.append(answer)
            node = self.client.find_node_by_id(1465147)
            answer = Answer(self.get_entity_name(node), [node], 0.6)
            answer_list.append(answer)
            node = self.client.find_node_by_id(2217)
            answer = Answer(self.get_entity_name(node), [node], 0.1)
            answer_list.append(answer)
            node = self.client.find_node_by_id(2805)
            answer = Answer(self.get_entity_name(node), [node], 0.1)
            answer_list.append(answer)
            time.sleep(3)
        answer_set = AnswerSet(answer_list=answer_list)
        return answer_set

    def get_entity_name(self, node):
        if node.has_key('name'):
            name = node.get('name')
        elif node.has_key('labels_en'):
            name = node.get('labels_en')
        else:
            name = ''
        return name
