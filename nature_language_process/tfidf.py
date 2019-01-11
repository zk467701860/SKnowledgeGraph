#!/usr/bin/python
# -*- coding: UTF-8 -*-
#此文件仅提供text进行基于word2vec的特征抽取的类，并且提供NLP相关处理办法

import gensim
import os
import sys
import json


class TF_IDFModel():

    def loadTF_IDF(self,type = 0):
        #type = 0 : api, type = 1 : wiki, type = 2 : total
        # print("TF_IDF LOADING...")
        dict_name = ["apidict","wikidict","dict"]
        dict_dir = "./model/"
        dict_path = dict_dir + dict_name[type]
        dict = gensim.corpora.Dictionary.load(dict_path)
        self.tfidfmodel = gensim.models.TfidfModel.load("./model/" + dict_name[type] + "_tfidf.model")
        self.lsimodel = gensim.models.LsiModel.load("./model/" + dict_name[type] + "_lsi.model")
        self.type = type
        self.dict = dict
        print("GET TF_IDF MODEL.")

    def competeSimilarity(self,text1,text2):
        corpus_list1 = self.dict.doc2bow(text1.split(" "))
        corpus_list2 = self.dict.doc2bow(text2.split(" "))
        corpus_tfidf1 = [self.tfidfmodel[corpus_list1]]
        corpus_tfidf2 = self.tfidfmodel[corpus_list2]
        corpus = gensim.corpora.MmCorpus('./model/apidict_corpuse.mm')
        tfidf = self.tfidfmodel[corpus]
        print("the tf-idf of text1:" + str(corpus_tfidf1))
        print("the tf-idf of text1:" + str(corpus_tfidf2))
        index = gensim.similarities.MatrixSimilarity(corpus_tfidf1)
        #index = gensim.similarities.MatrixSimilarity(tfidf)
        sims = index[corpus_tfidf2]
        print(sims)
        return sims

    def get_Word_TF_IDF(self,word):
        text = [word]
        vec = self.dict.doc2bow(text)
        tfidf = self.tfidfmodel[vec]
        if len(tfidf) == 0:
            return None
        else:
            return tfidf[0][1]

    def train_from_two_file(self,fname1,fname2):
        with open(fname1) as f1:
            with open(fname2) as f2:
                texts1 = json.loads(f1.read())
                texts2 = json.loads(f2.read())
            texts1 = texts1 + texts2
            texts1 = [tokens.split(" ") for tokens in texts1]
            self.trainTF_IDF(texts1,2)

    def trainFile(self,fname,type = 0):
        with open(fname) as f:
            texts = json.loads(f.read())
            texts = [tokens.split(" ") for tokens in texts]
            self.trainTF_IDF(texts,type)

    def trainTF_IDF(self,texts,type = 0):
        #type = 0 : api, type = 1 : wiki, type = 2 : total
        print("TF_IDF Training...")
        dict_name = ["apidict","wikidict","dict"]
        dict_dir = "./model/"
        dict_path = dict_dir + dict_name[type]
        print(dict_path)
        dict = gensim.corpora.Dictionary.load(dict_path)
        corpus_list = [dict.doc2bow(text) for text in texts]
        gensim.corpora.MmCorpus.serialize('./model/'+ dict_name[type] +'_corpuse.mm', corpus_list)
        corpus_tfidf = []
        tfidfModel = gensim.models.TfidfModel(corpus=corpus_list, id2word={}, dictionary=dict)
        tfidfModel.save("./model/"+ dict_name[type] + "_tfidf.model")
        corpus_tfidf = [tfidfModel[doc] for doc in corpus_list]
        print("tfidf finish.")
        lsi_model = gensim.models.LsiModel(corpus = corpus_tfidf,
                            id2word = dict,
                            num_topics=1000)
        lsi_model.save("./model/"+ dict_name[type] + "_lsi.model")
        print("lsi finish.")
        return tfidfModel,lsi_model

class TextClassification():

    def readApiText(self,fname):
        dictionary = gensim.corpora.Dictionary()
        with open(fname,"r") as f:
            data = json.loads(f.read())
            for line in data:
                #get dictionary from text
                texts = [line.split(" ")]
                dic = self.getDictionary(texts)
                dictionary.merge_with(dic)
        print(dictionary.token2id)
        dictionary.save("./model/apidict")
        print(dictionary.dfs)
        return dictionary

    def readWiki(self,fname):
        dictionary = gensim.corpora.Dictionary()
        with open(fname,"r") as f:
            data = json.loads(f.read())
            for line in data:
                #get dictionary from text
                texts = [line.split(" ")]
                dic = self.getDictionary(texts)
                dic_transfer = dictionary.merge_with(dic)
        print(dictionary.dfs)
        dictionary.save("./model/wikidict")
        return dictionary


    @staticmethod
    def getDictionary(texts):
        '''
        return a dictionary, this class is imported from gensim, we can use .token2id get some informations likes[{"keyword":ID},...]
        @paragraph:texts:[[word1,...],...]
        '''
        print("Dictionary establish...")
        dic = gensim.corpora.Dictionary(texts)
        #dic.save("../model/dict")
        return dic

    @staticmethod
    def TF_IDF(dictionary,text):
        #transfer text to vectors, the result has format likes [(ID,appear_times),...]
        #@paragraphs: text
        return dictionary.doc2bow(text.split())

if __name__ == "__main__":
    train_dir = "./data"
    apipath = train_dir + "/api_text.json"
    wikipath = train_dir + "/software_related_wiki_text.json"
    model = TextClassification()
    dict1 = model.readApiText(apipath)
    dict2 = model.readWiki(wikipath)
    dict1.merge_with(dict2)
    dict1.save("./model/dict")
    print(dict1.dfs)
    tfidfModel = TF_IDFModel()
    tfidfModel.trainFile(apipath)
    tfidfModel.trainFile(wikipath)
    tfidfModel.train_from_two_file(apipath,wikipath)
    tfidfModel.loadTF_IDF(2)
    tfidfModel.get_Word_TF_IDF("Human")
    tfidfModel.competeSimilarity("python and C","Human do well")