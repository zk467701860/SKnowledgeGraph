#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import traceback
from multiprocessing import Pool

import nltk
from bs4 import BeautifulSoup, Comment
from nltk.stem import WordNetLemmatizer

# from multiprocessing.pool import ThreadPool as Pool
if sys.version_info.major == 2:
    import types
    import copy_reg


    def _pickle_method(m):
        if m.im_self is None:
            return getattr, (m.im_class, m.im_func.func_name)
        else:
            return getattr, (m.im_self, m.im_func.func_name)


    copy_reg.pickle(types.MethodType, _pickle_method)


class TextPreprocessor(object):
    PATTERN_METHOD = re.compile(
        r'[_$a-zA-Z][_$a-zA-Z0-9]*\([_$a-zA-Z0-9, ]*\)')
    # pattern_arg = re.compile(r'(?P<Method>.+) ?\((?P<Args>.+)?\)')
    PATTERN_LIST = [
        re.compile(r'[0-9+-:#]+'),
        re.compile(r'[/\\*(),=?<>"\[\]]|0x|\\u|\\x'),
        re.compile(r'.*([a-zA-Z])\1{3,}')
    ]
    STRIP_STR = ' ’!"$%&\'()*,-./:;<=>?‘“”？，；…@[\\]^_`{|}~'
    UNKNOWN = "_UNKNOWN_"

    STOP_LIST = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
                     'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
                     'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
                     'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
                     'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a',
                     'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by',
                     'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
                     'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                     'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
                     'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
                     'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
                     'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
                     'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn',
                     'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn'])

    def __init__(self, workers_num=8, min_count=5):
        self.workers_num = workers_num
        self.vocab_dict = {}
        self.wnl = WordNetLemmatizer()
        self.min_count = min_count

    def html_tag_filter(self, html):
        soup = BeautifulSoup(html, "lxml")
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]
        [blockquote.extract() for blockquote in soup('blockquote')]
        for code in soup("code"):
            code_text = code.get_text()
            if not len(code_text.split()) <= 3 and not TextPreprocessor.PATTERN_METHOD.match(code_text):
                code.extract()
                continue
        return soup.get_text(separator=" ")

    def illegal_word_filter(self, text):
        words = []
        for w in nltk.word_tokenize(text):
            try:
                ## todo,fix the problem about 'ascii' codec can't decode byte
                w = self.wnl.lemmatize(w.lower().strip(TextPreprocessor.STRIP_STR))
                if len(w) == 0:
                    continue
                if w in TextPreprocessor.STOP_LIST:
                    continue
                matched = False
                for pattern in TextPreprocessor.PATTERN_LIST:
                    if pattern.match(w):
                        matched = True
                        break
                if matched:
                    continue
                words.append(w)
            except Exception:
                traceback.print_exc()

        if len(words) == 0:
            return ""
        return " ".join(words)

    def frequency_filter(self, text):
        if self.min_count == 1:
            return text
        words = []
        for w in text.split():
            if self.vocab_dict.get(w, 0) >= self.min_count:
                words.append(w)
        if len(words) == 0:
            return ""
        return " ".join(words)

    def html_tag_filter_by_key(self, data, key):
        data[key] = self.html_tag_filter(data[key])
        return data

    def illegal_word_filter_by_key(self, data, key):
        data[key] = self.illegal_word_filter(data[key])
        return data

    def frequency_filter_by_key(self, data, key):
        data[key] = self.frequency_filter(data[key])
        return data

    def batch_html_tag_filter_by_key(self, data_list, key):
        result_list = []
        for data in data_list:
            result_list.append(self.html_tag_filter_by_key(data, key))
        return result_list

    def batch_illegal_word_filter_by_key(self, data_list, key):
        result_list = []
        for data in data_list:
            result_list.append(self.illegal_word_filter_by_key(data, key))
        return result_list

    def batch_frequency_filter_by_key(self, data_list, key):
        result_list = []
        for data in data_list:
            result_list.append(self.frequency_filter_by_key(data, key))
        return result_list

    @staticmethod
    def sort_by_value(d):
        items = d.items()
        backitems = [[v[1], v[0]] for v in items]
        backitems.sort(reverse=True)
        new_d = {}
        for item in backitems:
            new_d[item[1]] = item[0]
        return new_d

    def filter(self, dataset, mode='111'):
        '''
        mode=100 filter html
        mode=010 filter illegal word
        mode=001 filter low freauency word
        add these three value
        '''
        if len(mode) != 3:
            print("Error: len(mode) != 3.")
            exit(1)
        filter_freq = int(mode[0])
        filter_illegal = int(mode[1])
        filter_html = int(mode[2])

        batch_size = len(dataset) // self.workers_num + 1
        if filter_html == 1:
            with Pool(self.workers_num) as pool:
                dataset = pool.map(self.html_tag_filter, dataset, batch_size)
        if filter_illegal == 1:
            with Pool(self.workers_num) as pool:
                dataset = pool.map(self.illegal_word_filter, dataset, batch_size)

        for t in dataset:
            for w in t.split():
                self.vocab_dict[w] = self.vocab_dict.get(w, 0) + 1

        if filter_freq == 1:
            with Pool(self.workers_num) as pool:
                dataset = pool.map(self.frequency_filter, dataset, batch_size)
            for key in self.vocab_dict.keys():
                if self.vocab_dict[key] < self.min_count:
                    self.vocab_dict.pop(key)
        self.vocab_dict = TextPreprocessor.sort_by_value(self.vocab_dict)
        vocab = set(self.vocab_dict.keys())
        return dataset, vocab

    def filter_by_key(self, dataset, key, mode='111'):
        '''
        mode=100 filter html
        mode=010 filter illegal word
        mode=001 filter low freauency word
        add these three value
        '''
        if len(mode) != 3:
            print("Error: len(mode) != 3.")
            exit(1)
        filter_freq = int(mode[0])
        filter_illegal = int(mode[1])
        filter_html = int(mode[2])

        size = len(dataset)
        batch_size = size // self.workers_num + 1
        if filter_html == 1:
            returns = []
            pool = Pool(self.workers_num)
            for i in range(self.workers_num):
                start = i * batch_size
                end = start + batch_size
                end = size if end > size else end
                ret = pool.apply_async(
                    self.batch_html_tag_filter_by_key, args=(dataset[start:end], key))
                returns.append(ret)
            pool.close()
            pool.join()
            dataset = []
            for ret in returns:
                dataset.extend(ret.get())
        if filter_illegal == 1:
            returns = []
            pool = Pool(self.workers_num)
            for i in range(self.workers_num):
                start = i * batch_size
                end = start + batch_size
                end = size if end > size else end
                ret = pool.apply_async(
                    self.batch_illegal_word_filter_by_key, args=(dataset[start:end], key))
                returns.append(ret)
            pool.close()
            pool.join()
            dataset = []
            for ret in returns:
                dataset.extend(ret.get())
        for d in dataset:
            for w in d[key].split():
                self.vocab_dict[w] = self.vocab_dict.get(w, 0) + 1
        if filter_freq == 1:
            returns = []
            pool = Pool(self.workers_num)
            for i in range(self.workers_num):
                start = i * batch_size
                end = start + batch_size
                end = size if end > size else end
                ret = pool.apply_async(
                    self.batch_frequency_filter_by_key, args=(dataset[start:end], key))
                returns.append(ret)
            pool.close()
            pool.join()
            dataset = []
            for ret in returns:
                dataset.extend(ret.get())
            for key in self.vocab_dict.keys():
                if self.vocab_dict[key] < self.min_count:
                    self.vocab_dict.pop(key)

        self.vocab_dict = TextPreprocessor.sort_by_value(self.vocab_dict)
        vocab = set(self.vocab_dict.keys())
        return dataset, vocab
