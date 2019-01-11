# coding: utf-8
import traceback

import numpy as np
import pandas as pd

from db.engine_factory import EngineFactory
from db.model import DocumentSentenceText, DocumentSentenceTextAnnotation


class AnnoationResultExporter:
    def __init__(self):
        self.session = None
        self.df = None
        self.df_same=None
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
                    #数据库从小到大遍历，只要覆盖，就能取同一个人对同一句子的最新标注记录取
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

    def write_df(self, path):
        self.df.to_json(path, orient='records', force_ascii=False)

    def merge_vote_result_to_json(self, st_dic):
        unique_set = self.unique_set
        loop = 0
        for unique_code in unique_set:
            result_list = np.array([0, 0, 0, 0])
            name_vot_list_dic = st_dic[unique_code]
            for vote_list in name_vot_list_dic.values():
                result_list[0] += vote_list[0]
                result_list[1] += vote_list[1]
                result_list[2] += vote_list[2]
                result_list[3] += vote_list[3]

            vote_type = np.argmax(result_list)
            doc_id, sentence_index = self.get_doc_id_sentence_index_by_unique_code(unique_code)
            java_api_document_sentence_text = self.get_id_text_by_doc_id_sentence_index(doc_id, sentence_index)
            if java_api_document_sentence_text == None:
                continue
            sentence_id = java_api_document_sentence_text.id
            text = java_api_document_sentence_text.text
            self.df.loc[loop] = [sentence_id, doc_id, sentence_index, text, vote_type]
            loop += 1

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

    def get_id_text_by_doc_id_sentence_index(self, doc_id, sentence_index):
        try:
            return self.session.query(DocumentSentenceText).filter_by(doc_id=doc_id,
                                                                      sentence_index=sentence_index).first()
        except Exception:
            traceback.print_exc()
            return None

    def export_annotation_result(self):
        self.unique_set = set()

        statistic_dic = self.get_statistic_dic()
       #self.merge_vote_result_to_json(statistic_dic)
        annotation_status_list = self.count_annotation_status(statistic_dic)
        self.statiscs_annotation_status(annotation_status_list)
        #将所有的分类转为json（包括：单人标注、有效、有分歧）
        #self.write_df('annotation_sentence_classification.json')
        #将可用的分类句子转为json
        self.df_same.to_json('annotation_sentence_vote_valid.json', orient='records', force_ascii=False)
        #self.df_disagree_type3.to_excel('dis_type3.xls')

    def statiscs_annotation_status(self, annotation_status_list):
        with open("annotation_status_list.json", "w") as json_file:
            #print(annotation_status_list)
            # json.dump(annotation_status_list, json_file)
            json_file.write(str(annotation_status_list))
            same_num = 0
            two_same=0
            single_annotation_num = 0
            less_agree_num = 0
            less_agree_doc_id_sentence_index = []
            single_annotation_doc_id_list = []
            type_3=0
            for status in annotation_status_list:
                if status["max_vote_num"] == 2  and status["vote_count"]==2 and status["agree_rate"] ==1:
                    two_same= two_same + 1
                if status["max_vote_num"] >= 2 and status["agree_rate"] > 0.66:
                    if status["vote_type"]==3:
                        status["vote_type"]=1
                    self.df_same.loc[same_num] = [status["sentence_id"],status["doc_id"], status["sentence_index"], status["text"],status["vote_type"]]
                    same_num = same_num + 1
                if status["vote_count"] == 1:
                    # if status["vote_type"]==3:
                    #     self.df_single_type3.loc[type_3] = [status["doc_id"], status["sentence_index"]]
                    #     type_3+=1;
                    single_annotation_num = single_annotation_num + 1
                    single_annotation_doc_id_list.append(status["doc_id"])
                if status["vote_count"] > 1 and status["agree_rate"] < 0.66:
                    less_agree_num = less_agree_num + 1
                    less_agree_doc_id_sentence_index.append((status["doc_id"], status["sentence_index"]))

            print("single_annotation_num=%d", single_annotation_num)
            print("same_num=%d", same_num)
            print("two_same=%d", two_same)
            print("less_agree_num=%d", less_agree_num)


            with open("not_agree_sentence_list.txt", "w") as f:
                for (doc_id, sentence_index) in less_agree_doc_id_sentence_index:
                    f.write("doc_id=%d sentence_index=%d\n" % (doc_id, sentence_index))

            with open("single_annotation_doc_id_list.txt", "w") as f:
                for doc_id in single_annotation_doc_id_list:
                    f.write("doc_id=%d\n" % (doc_id,))

    def init(self):
        self.session = EngineFactory.create_session()
        self.df = pd.DataFrame(columns=['sentence_id', 'doc_id', 'sentence_index', 'text', 'type'])
        self.df_same = pd.DataFrame(columns=['sentence_id', 'doc_id', 'sentence_index', 'text', 'vote_type'])


if __name__ == "__main__":
    exporter = AnnoationResultExporter()
    exporter.init()
    exporter.export_annotation_result()
