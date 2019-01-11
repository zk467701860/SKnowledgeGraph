import traceback
from math import ceil
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, MetaData, ForeignKey, DateTime, Index, Boolean, func, Table, SmallInteger
from sqlalchemy import text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from json import loads
from engine_factory import EngineFactory
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.externals import joblib
from model import Wikipedia
from word2vec import TextClassification
import os
import json
import gensim
from scipy.sparse import csr_matrix
from sklearn import svm

class TrainSVM():
	documents = []
	tags = []
	def __init__(self):
		'''
		get the texts
		@paragram rootdir:path of train datas
		'''
		documents = []
		tags = []

	def initByFile(self,rootdir):
		'''
		get the texts
		@paragram rootdir:path of train data
		'''
		print("Reading")
		r = os.walk(rootdir)
		for parent,dirnames,filenames in r:
			for filename in  filenames:
				fullpath = os.path.join(parent,filename)
				with open(fullpath,"r",encoding='UTF-8',errors="ignore") as f:
					setting = json.load(f)
					self.documents = setting[0]
					print(self.documents[0])
					self.tags = setting[1]

	def initByMySQL(self,session):
		'''
		get doc from mySQL, it's used for geting predict texts
		Maybe I need to think of How to deal with all the docs in mySQL
		'''
		totalnum = Wikipedia.getNumOf(session)
	
	@staticmethod
	def trainDictionaryByDoc(doc):
		'''
		@paragram:doc-[[text],...]
		@return:dictionary
		'''
		dictionary = TextClassification.getDictionary(doc)
		print("dic:" + str(dictionary))
		return dictionary
		
	@staticmethod
	def trainDictionaryByGlobaldata(session):
		totalnum = Wikipedia.getNumOf(session)
		print(totalnum)
		# get dictionary from doc
		dictionary = TextClassification.getDictionary([["computer","science"]])
		for ii in range(0,ceil(totalnum/1000)):
			doc_list = Wikipedia.searchPageOf(session,1000,ii)
			print(type(doc_list))
			documents = []
			for doc in doc_list:
				documents = documents + TextClassification.divideIntoWords([doc.content])
			dic = TextClassification.getDictionary(documents)
			dic.filter_extremes(no_above=0.5)
			print(dic)
			dic_transfer = dictionary.merge_with(dic)
		#dictionary.filter_extremes(no_below=5) 
		#dictionary.compacity() 
		dictionary.save("../model/dict")	
	
	@staticmethod
	def getFeature(dic,texts):
		print("=======getFeature=======")
		k = TextClassification.divideIntoWords(texts)
		#print(k)
		corpus_list = [dic.doc2bow(text) for text in k]
		#print(corpus_list)
		gensim.corpora.MmCorpus.serialize('../model/corpuse.mm', corpus_list)
		corpus_tfidf = []
		tfidfModel = gensim.models.TfidfModel(corpus=corpus_list, id2word={}, dictionary=dic)
		tfidfModel.save("../model/tfidf.model")
		corpus_tfidf = [tfidfModel[doc] for doc in corpus_list]
		#for item in corpus_tfidf:
		#	print(item)
		print("tfidf finish...")
		#corpus_tfidf.save("../model/data.tfidf")
		lsi_model = gensim.models.LsiModel(corpus = corpus_list, 
                            id2word = dic, 
                            num_topics=2)
		corpus_lsi = [lsi_model[doc] for doc in corpus_list]
		print("lsi finish...")
		data = []
		rows = []
		cols = []
		line_count = 0
		print(len(corpus_tfidf))
		#for line in corpus_lsi:
		for line in corpus_tfidf:
			for elem in line:
				rows.append(line_count)
				cols.append(elem[0])
				data.append(elem[1])
			line_count += 1
		lsi_sparse_matrix = csr_matrix((data,(rows,cols)))
		lsi_matrix = lsi_sparse_matrix.toarray()
		print(lsi_matrix)
		print("Get Feature!")
		
		return lsi_matrix
	
	@staticmethod
	def trainSVM(train_tag,lsi_matrix):
		print("Train Starting...")
		clf = svm.SVC(kernel='rbf',gamma = "auto")
		#clf = svm.LinearSVC()
		clf_res = clf.fit(lsi_matrix,train_tag)
		joblib.dump(clf_res,'../model/svm.model')
	
	#@staticmethod
	def predictBySVM(self, documents):
		dic = gensim.corpora.Dictionary.load('../model/dict')
		feature = self.getFeature(dic,documents)
		clf_res = joblib.load('../model/svm.model')
		pred  = clf_res.predict(feature)
		print(pred)
		return pred
		#train_pred  = clf_res.predict(train_set)
		#test_pred   = clf_res.predict(test_set)
	
	#@staticmethod
	def emmm(self, filepath):
		with open(filepath,"r", encoding = "utf-8") as f:
			test_dataset = json.load(f)
			if test_dataset == None:
				return
		doc = test_dataset[0]
		tag = test_dataset[1]
		#print(doc)
		print("Deal Test dataset starting...")
		print("total:" + str(len(doc)) + " type: " + str(type(doc)))
		pre_tag = self.predictBySVM(doc)
		p1 = 0 #真标为假
		p2 = 0 #真标为真
		p3 = 0 #假标为真
		p4 = 0 #假标为假
		for i in range(0,len(tag)):
			if tag[i] == pre_tag[i]:
				if tag[i] == 0:
					p4 += 1
				else:
					p2 += 1
			else:
				if tag[i] == 0:
					p3 += 1
				else:
					p1 += 1
		print("predictTag is right(present%): " + str(p2+p4) +"(" + str((p2+p4)/len(tag)) + ")")
		print("Predict True: pre _tag is 1:" + str(p2))
		print("Predict True: pre _tag is 0:" + str(p4))
		print("Predict False: pre_tag is 1 but tag is 0: " + str(p3))
		print("Predict False: pre_tag is 0 but tag is 1: " + str(p1))	
		print("Tag-1:" + str(p1+p2))
		print("Tag-0:" + str(p3+p4))

if __name__ == "__main__":
	
	c = TrainSVM()
	c.initByFile(r"C:\Users\apple\Desktop\SKnowledgeGraph-master\SKnowledgeGraph-master\initgraph\train_data")
	dic = c.trainDictionaryByDoc(c.documents)
	feature = c.getFeature(dic,c.documents)
	c.trainSVM(c.tags,feature)
	#
	#c.predictBySVM(c.documents)
	
	c.emmm(r"C:\Users\apple\TrainData\dataset\document_classification\test.json")