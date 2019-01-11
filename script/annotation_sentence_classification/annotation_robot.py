# coding: utf-8
import traceback

import numpy as np
import pandas as pd

from db.engine_factory import EngineFactory
from db.model import DocumentSentenceText, DocumentSentenceTextAnnotation


class AnnoationRobot:
    def __init__(self):
        self.session = None
        self.unique_set = None

    def get_statistic_dic(self):
        sentence_text_annotation_list = self.session.query(DocumentSentenceTextAnnotation).all()
        statistic_dic = {}
        counter = 0
        for sentence_text_annotation in sentence_text_annotation_list:

            try:
                doc_id = sentence_text_annotation.doc_id
                sentence_index = sentence_text_annotation.sentence_index
                type = sentence_text_annotation.type
                if sentence_text_annotation.username is not None and sentence_text_annotation.username != '':
                    username = sentence_text_annotation.username
                else:
                    username = '?'
                unique_code = str(doc_id) + '_' + str(sentence_index)
                self.unique_set.add(unique_code)
                if statistic_dic.has_key(unique_code):
                    # if (statistic_dic[unique_code]).has_key(username):
                    #     ((statistic_dic[unique_code])[username])[type] += 1
                    # else:
                    # 数据库从小到大遍历，只要覆盖，就能取同一个人对同一句子的最新标注记录取
                    temp_list = [0, 0, 0, 0]
                    temp_list[type] = 1
                    (statistic_dic[unique_code])[username] = temp_list
                else:
                    temp_list = [0, 0, 0, 0]
                    temp_list[type] = 1
                    statistic_dic[unique_code] = {username: temp_list}
                counter += 1
            except Exception, err:
                print 'Exception:\t', str(Exception)
                print 'e.message:\t', err.message
        print(counter)
        return statistic_dic

    def get_doc_id_sentence_index_by_unique_code(self, unique_code):
        doc_id, sentence_index = unique_code.split('_', 1)
        try:
            int_doc_id = int(doc_id)
            int_sentence_index = int(sentence_index)
            return int_doc_id, int_sentence_index
        except Exception, err:
            print 'Exception:\t', str(Exception)
            print 'e.message:\t', err.message
            return None

    def get_id_text_by_doc_id_sentence_index(self, doc_id, sentence_index):
        try:
            return self.session.query(DocumentSentenceText).filter_by(doc_id=doc_id,
                                                                      sentence_index=sentence_index).first()
        except Exception:
            traceback.print_exc()
            return None

    def count_annotation_status(self, st_dic):
        """
        count how many person are agree on the annotation type
        :param st_dic:
        :return:
        """
        result = []
        unique_set = self.unique_set
        for unique_code in unique_set:
            result_list = np.array([0, 0, 0, 0])
            name_vot_list_dic = st_dic[unique_code]

            for vote_list in name_vot_list_dic.values():
                result_list[0] += vote_list[0]
                result_list[1] += vote_list[1]
                result_list[2] += vote_list[2]
                result_list[3] += vote_list[3]

            vote_type = np.argmax(result_list)
            max_vote_num = np.max(result_list)
            count = np.sum(result_list)
            agree_rate = 0
            if count != 0:
                agree_rate = float(max_vote_num) / float(count)
            doc_id, sentence_index = self.get_doc_id_sentence_index_by_unique_code(unique_code)
            java_api_document_sentence_text = self.get_id_text_by_doc_id_sentence_index(doc_id, sentence_index)
            if java_api_document_sentence_text == None:
                continue
            sentence_id = java_api_document_sentence_text.id
            text = java_api_document_sentence_text.text
            annotation_status = {
                "sentence_id": sentence_id,
                "doc_id": doc_id,
                "sentence_index": sentence_index,
                "text": text,
                "vote_type": vote_type,
                "vote_count": count,
                "max_vote_num": max_vote_num,
                "agree_rate": agree_rate,
            }
            result.append(annotation_status)

        return result

    def add_function(self, annotation_status_list):
        """
        make type of fist sentenece to be function on single and disagree documents
        :param st_dic:
        :return:
        """
        single_add_first = 0
        disagree_add_first = 0
        for status in annotation_status_list:
            if status["sentence_index"] == 0 and status["vote_count"] == 1:
                single_add_first = single_add_first + 1;
                sentence_text_annotation = DocumentSentenceTextAnnotation(status["doc_id"], status["sentence_index"], 1,
                                                                          "AnnotationRobot")
                sentence_text_annotation.find_or_create(self.session)
            if status["sentence_index"] == 0 and status["vote_count"] > 1 and status["agree_rate"] < 0.66:
                disagree_add_first = disagree_add_first + 1;
                sentence_text_annotation = DocumentSentenceTextAnnotation(status["doc_id"], status["sentence_index"], 1,
                                                                          "AnnotationRobot")
                sentence_text_annotation.find_or_create(self.session)

        print ("single first sentence to be function :", single_add_first)
        print ("disagree first sentence to be function :", disagree_add_first)

    def add_directive(self, annotation_status_list):
        """
        match keywords to make type of sentence to be directive on single and disagree documents
        :param st_dic:
        :return:
        """
        single_add_directive = 0
        disagree_add_directive = 0
        for status in annotation_status_list:
            if status["sentence_index"] != 0 and status["vote_count"] == 1 and self.directive_match(status["text"]) == True:
                single_add_directive = single_add_directive + 1
                sentence_text_annotation = DocumentSentenceTextAnnotation(status["doc_id"], status["sentence_index"], 2,
                                                                          "AnnotationRobot2")
                sentence_text_annotation.find_or_create(self.session)
            if status["sentence_index"] != 0 and status["vote_count"] > 1 and status["agree_rate"] < 0.66 and self.directive_match(status["text"]) == True:
                disagree_add_directive = disagree_add_directive + 1
                sentence_text_annotation = DocumentSentenceTextAnnotation(status["doc_id"], status["sentence_index"], 2,
                                                                          "AnnotationRobot3")
                sentence_text_annotation.find_or_create(self.session)

        print ("single sentences to be directive :", single_add_directive)
        print ("disagree sentences to be directive :", disagree_add_directive)

    @staticmethod
    def directive_match(sentence):
        key_words = ["parameter", "exception","return", "must", "when", "where", "should", "rather than", "better",
                     "preferable", "can't", "should't"]
        sentence = sentence.lower()
        for key in key_words:
            flag = sentence.find(key)
            if flag != -1:
                return True
        return False

    def init(self):
        self.session = EngineFactory.create_session()
        self.df = pd.DataFrame(columns=['sentence_id', 'doc_id', 'sentence_index', 'text', 'type'])

    def add_annotation_robot(self):
        self.unique_set = set()
        statistic_dic = self.get_statistic_dic()
        annotation_status_list = self.count_annotation_status(statistic_dic)
        self.add_function(annotation_status_list)
        self.add_directive(annotation_status_list)


if __name__ == "__main__":
    exporter = AnnoationRobot()
    exporter.init()
    exporter.add_annotation_robot()
