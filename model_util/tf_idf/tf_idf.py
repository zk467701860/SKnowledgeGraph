#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 此文件仅提供text进行基于word2vec的特征抽取的类，并且提供NLP相关处理办法
import json
import gensim
import numpy as np


def array_transfer(array, dia=128):
    new_array = np.zeros(dia)
    for item in array:
        new_array[item[0]] = item[1]
    return new_array


class TFIDFModel:
    def __init__(self, dict_dir="./model_util/tf_idf/model/"):
        """

        :param dict_dir: the dir where dictionary is stored
        """
        self._dict = gensim.corpora.Dictionary()
        self._type = 2
        self._tf_idf_model = None
        self._lsi_model = None

    @property
    def dict(self):
        return self._dict

    @property
    def type(self):
        return self._type

    @property
    def tf_idf_model(self):
        return self._tf_idf_model

    @property
    def lsi_model(self):
        return self._lsi_model

    def load(self, dict_dir="./model_util/tf_idf/model/", dict_type=0):
        """
        load the model, you can use it if you have already trained
        :param dict_dir: dict_dir: the dir where dictionary is stored
        :param dict_type: dict_type:data_type[0]=api, data_type[1] =wiki, data_type[2]=total
        """
        dict_name = ["apidict", "wikidict", "dict"]
        dict_path = dict_dir + dict_name[dict_type]
        self._dict = gensim.corpora.Dictionary.load(dict_path)
        self._type = type
        self._tf_idf_model = gensim.models.TfidfModel.load(dict_path + "_tfidf.model_util")
        self._lsi_model = gensim.models.LsiModel.load(dict_path + "_lsi.model_util")

    def similarity_between_two_sentence(self, text1, text2):
        """
        get similarity between two sentences
        :param text1: String
        :param text2: String
        :param path: the path where you want to save your corpus file
        :return sims: float
        """
        corpus_list1 = self.dict.doc2bow(text1.split(" "))
        corpus_list2 = self.dict.doc2bow(text2.split(" "))
        corpus_lsi_1 = [self._lsi_model[self.tf_idf_model[corpus_list1]]]
        corpus_lsi_2 = self._lsi_model[self.tf_idf_model[corpus_list2]]
        index = gensim.similarities.MatrixSimilarity(corpus_lsi_1)
        sims = index[corpus_lsi_2]
        return sims

    def get_word_tf_idf(self, word):
        """
        :param word:
        :return: ts_idf of the word: float
        """
        text = [word]
        vec = self.dict.doc2bow(text)
        tf_idf = self._tf_idf_model[vec]
        if len(tf_idf) == 0:
            return 0
        else:
            return tf_idf[0][1]

    def get_sentence_vec(self,text):
        """

        :param text:
        :return:
        """
        word_vec = self.dict.doc2bow(text.lower().split(" "))
        tf_idf_vec = self._tf_idf_model[word_vec]
        lsi_vec = self._lsi_model[word_vec]
        return array_transfer(lsi_vec)


    def train_in_total(self, file_path_1, file_path_2):
        """
        train from two files
        :param file_path_1:
        :param file_path_2:
        :param dict_type:
        """
        with open(file_path_1) as f1:
            with open(file_path_2) as f2:
                texts = json.loads(f1.read()) + json.loads(f2.read())
                texts = [tokens.split(" ") for tokens in texts]
                self.train_tf_idf(texts, dict_type=2)

    def train_file(self, file_path, dict_type=0):
        """
        train one file
        :param file_path:
        :param dict_type:
        """
        with open(file_path) as f:
            texts = json.loads(f.read())
            texts = [tokens.split(" ") for tokens in texts]
            self.train_tf_idf(texts, dict_type)

    def train_tf_idf(self, texts, dict_type=0, dict_dir="./model_util/tf_idf/model/"):
        """
        :param texts: training docs
        :param dict_type: the type of dict
        :param dict_dir: the dir where dictionary is stored
        :return:
        """
        print("TF-IDF Training...")
        dict_name = ["apidict", "wikidict", "dict"]
        dict_path = dict_dir + dict_name[dict_type]
        _dict = gensim.corpora.Dictionary.load(dict_path)
        corpus_list = [_dict.doc2bow(text) for text in texts]
        gensim.corpora.MmCorpus.serialize(dict_path + '_corpus.mm', corpus_list)
        _tf_idf_model = gensim.models.TfidfModel(corpus=corpus_list, id2word={}, dictionary=_dict)
        _tf_idf_model.save(dict_path + "_tfidf.model_util")
        corpus_tf_idf = [_tf_idf_model[doc] for doc in corpus_list]
        print("TF-IDF Training Finished.")
        #print(corpus_tf_idf)
        _lsi_model = gensim.models.LsiModel(corpus=corpus_tf_idf, id2word=_dict, num_topics=128)
        #for item in _lsi_model[corpus_tf_idf]:
        #    print item
        _lsi_model.save(dict_path + "_lsi.model_util")
        print("lsi finish.")
        return _tf_idf_model, _lsi_model


class TextDictionary:
    def __init__(self):
        pass

    def init_default_dict(self, data_type=2):
        """
        init dictionary from default config
        :param data_type:
        :return:
        """
        if data_type == 0:
            self._api_dict = self.init_api_dict()
        elif data_type == 1:
            self._wiki_dict = self.init_wiki_dict()
        elif data_type == 2:
            self._api_dict, self._wiki_dict, self._total_dict = self.init_total_dict()
        else:
            return None

    def init_total_dict(self, api_data="./model_util/tf_idf/data/api_text.json",
                        wiki_data="./model_util/tf_idf/data/software_related_wiki_text.json",
                        dict_path="./model_util/tf_idf/model/dict"):
        """
        :param api_data:
        :param wiki_data:
        :param dict_path:
        :return:
        """
        api_dict = self.init_api_dict(api_data)
        wiki_dict = self.init_wiki_dict(wiki_data)
        total_dict = api_dict
        total_dict.merge_with(wiki_dict)
        total_dict.save(dict_path)
        return api_dict, wiki_dict, total_dict

    def init_api_dict(self, data_path="./model_util/tf_idf/data/api_text.json",
                      dict_path="./model_util/tf_idf/model/apidict"):
        dictionary = gensim.corpora.Dictionary()
        with open(data_path, "r") as f:
            data = json.loads(f.read())
            for line in data:
                # get dictionary from text
                texts = [line.split(" ")]
                dic = self.get_dictionary(texts)
                dictionary.merge_with(dic)
        dictionary.save(dict_path)
        return dictionary

    def init_wiki_dict(self, data_path="./model_util/tf_idf/data/software_related_wiki_text.json",
                       dict_path="./model_util/tf_idf/model/wikidict"):
        dictionary = gensim.corpora.Dictionary()
        with open(data_path, "r") as f:
            data = json.loads(f.read())
            for line in data:
                # get dictionary from text
                texts = [line.split(" ")]
                dic = self.get_dictionary(texts)
                dic_transfer = dictionary.merge_with(dic)
        dictionary.save(dict_path)
        return dictionary

    @staticmethod
    def get_dictionary(texts):
        """
        return a dictionary, this class is imported from gensim, we can use .token2id get some informations likes[{"keyword":ID},...]
        :param texts: [[word1,...],...]
        :return dict:
        """
        return gensim.corpora.Dictionary(texts)

    @staticmethod
    def tf_idf(dictionary, text):
        """
        transfer text to vector
        :param dictionary: dict
        :param text: string
        :return: word_vec:[(ID,appear_times),...]
        """
        return dictionary.doc2bow(text.split())


if __name__ == "__main__":
    train_dir = "./model_util/tf_idf/data/"
    apipath = train_dir + "api_text.json"
    wikipath = train_dir + "software_related_wiki_text.json"
    dictionary = TextDictionary()
    dictionary.init_default_dict(data_type=2)
    tfidfModel = TFIDFModel()
    tfidfModel.train_file(apipath, dict_type=0)
    tfidfModel.train_file(wikipath, dict_type=1)
    tfidfModel.train_in_total(apipath, wikipath)
    tfidfModel.load(dict_type=2)
    print tfidfModel.get_word_tf_idf("java")
    print tfidfModel.get_sentence_vec(
        "By using the EventHandler class instead of inner classes \
        for custom event handlers, you can avoid this problem."
    )
    print tfidfModel.similarity_between_two_sentence("By using the EventHandler class instead of inner classes for custom event handlers, you can avoid this problem",
        "Provides reference-object classes, which support a limited degree of interaction with the garbage collector.")
