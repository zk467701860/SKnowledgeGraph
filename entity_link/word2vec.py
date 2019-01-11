#!/usr/bin/python
# -*- coding: UTF-8 -*-
#此文件仅提供text进行基于word2vec的特征抽取的类，并且提供NLP相关的处理办法

import gensim
import logging
import os
from collections import defaultdict
import sys
import re
from scipy import sparse
from sklearn import svm
import numpy as np
from model import Wikipedia
import json
from nltk.corpus import stopwords

month = {'January', 'February', 'March', 'April', 'May', 'June', 'July', 'Augest', 'September', 'October', 'November', 'December',
		'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May.', 'June.', 'July.', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.'}
week = {'Monday', "Tuesday", "Wednesday", 'Thursday', 'Friday', 'Saturday', 'Sunday', 
		'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'}

class TextClassification(object):
	document = []
	def __init__(self, rootdir = None):
		#start logging
		logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
		#read all files in the root dir
		r = os.walk(rootdir)
		for parent,dirnames,filenames in r:
			for filename in  filenames:
				fullpath = os.path.join(parent,filename)
				with open(fullpath,"r",encoding='UTF-8',errors="ignore") as f:
					setting = json.load(f)
					self.document = setting[0]
	
	@staticmethod
	def divideIntoWords(documents):
		'''
		Preprocessing
		@paragraph:documents = [text1,...]
		@return:[[word1,...],...]
		cut the documents into words
		cut the paragraph into sentence,and then cut the sentence into words, after that, delete words in stop list
		use "NUM" replace all the numbersand use "DATE" replace all the date
		'''
		texts = []
		stoplist = set('for a of the and to in the'.split())
		for doc in documents:
			new_doc = []
			paragraphs = doc.split("\n")
			for p in paragraphs:
				#print(p)
				if len(p) > 0:
					sentences = re.split(r"[#_@$.!?:\"<>,\'\t|()-+*/%（）]", p)
					for s in sentences:
						words = re.split("[ \t\n\r\f\v-#_@$.!?:\"<>,\'|()-+*/\%（）]",s)
						for w in words:
							if w.isdigit():
								new_doc.append("NUM")
							elif w in month or w in week:
								new_doc.append("DATE")
							elif w in stoplist or w == '':
								continue
							else:
								new_doc.append(w.lower())
				#print(new_doc)
			texts.append([tokens for tokens in new_doc])
		return texts
		
	@staticmethod	
	def getDictionary(documents):
		'''
		return a dictionary, this class is imported from gensim, we can use .token2id get some informations likes[{"keyword":ID},...]
		@paragraph:texts:[[word1,...],...]
		'''
		print("Dictionary establish...")
		texts = []
		#stoplist = set('for a of the and to in the'.split())
		stoplist = list(set(stopwords.words('english')))
		for doc in documents:
			new_doc = []
			paragraphs = doc.split("\n")
			for p in paragraphs:
				#print(p)
				if len(p) > 0:
					sentences = re.split(r"[#_@$.!?:\"<>,\'\t|()-+*/%（）]", p)
					for s in sentences:
						words = re.split("[ \t\n\r\f\v-#$.!?:\"<>,\'|()+*%（）]",s)
						for w in words:
							if w.isdigit():
								new_doc.append("NUM")
							elif w in month or w in week:
								new_doc.append("DATE")
							elif w in stoplist or w == '':
								continue
							else:
								new_doc.append(w.lower())
				#print(new_doc)
			texts.append([tokens for tokens in new_doc])
		
		dic = gensim.corpora.Dictionary(texts, prune_at=20000)
		dic.filter_extremes(no_below=1, no_above=0.4)
		dic.save("../model/dict")
		return dic
	
	@staticmethod
	def TF_IDF(dictionary,text):
		#transfer text to vectors, the result has format likes [(ID,appear_times),...]
		#@paragraphs: text
		return dictionary.doc2bow(text.lower().split())
	
if __name__ == "__main__":
	traindata = "../train_data"
	model = TextClassification(traindata)
	#texts = model.divideIntoWords(model.document)
	dic = model.getDictionary(model.document)
	#print(texts)
	dic.filter_extremes(no_below=1, no_above=0.4)
	print(str(dic))
	dic.save("../model/dict")
	'''
	corpus_list = [dic.doc2bow(text) for text in texts]
	#print(corpus_list)
	gensim.corpora.MmCorpus.serialize('../model/corpuse.mm', corpus_list)
	corpus_tfidf = []
	tfidfModel = gensim.models.TfidfModel(corpus=corpus_list, id2word={}, dictionary=dic)
	tfidfModel.save("../model/tfidf.model")
	corpus_tfidf = tfidfModel[corpus_list]
	dia = len(tfidfModel.idfs)
	m = []
	for item in corpus_list:
		m.append(sparse2mar(item,dia))
	#print(m)
	corpus_tfidf.save("../model/data.tfidf") 
	tfidf = gensim.models.TfidfModel.load("../model/data.tfidf") 
	#print(tfidfModel.dfs) 
	#print(tfidfModel.idfs)
	'''

		
		