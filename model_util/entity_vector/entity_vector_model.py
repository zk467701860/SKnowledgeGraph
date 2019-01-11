# encoding: utf-8
import codecs
import json
import traceback

import numpy as np
from gensim import matutils
from gensim.models import KeyedVectors
from numpy.core.multiarray import dot

from shared.preprocess_data import TextPreprocessor


# reload(sys)
# sys.setdefaultencoding('utf8')


class EntityVectorModel:
    def __init__(self):
        pass

    @staticmethod
    def load(path, binary=False):
        if path is None:
            return None
        wv_from_text = None
        if binary == False:
            wv_from_text = KeyedVectors.load_word2vec_format(path, binary=False)  # C text format
        else:
            wv_from_text = KeyedVectors.load_word2vec_format(path, binary=True)
        return wv_from_text


class EntityVectorComputeModel:

    def __init__(self):
        self.wv = None
        self.text_preprocessor = TextPreprocessor(min_count=1)
        self.vocab = set([])

    def init_word2vec_model(self, path, binary=False):
        if path is None:
            return False
        wv_from_text = None
        if binary == False:
            wv_from_text = KeyedVectors.load_word2vec_format(path,
                                                             binary=False)  # C text format
        else:
            wv_from_text = KeyedVectors.load(path)

        self.wv = wv_from_text
        self.vocab = set(self.wv.vocab.keys())

        if self.wv:
            return True
        else:
            return False

    def get_vector_for_word(self, word):
        try:
            if self.wv:
                return self.wv[word]
        except Exception:
            traceback.print_exc()
        return None

    def train_mean_vector(self, input_path, output_path):
        data_set = None
        if self.is_init_word2vec() == False:
            print("word2vec model not loaded")
            return
        with codecs.open(input_path, 'r', 'utf-8') as f:
            data_set = json.load(f)
        self.train_mean_vector_from_corpus(data_set, output_path)

    def train_mean_vector_from_corpus(self, data_set, output_path):
        data_set = self.preprocess_list_text(data_set)
        result_list = []
        with codecs.open(output_path, 'w', 'utf-8') as f:
            for item in data_set:
                vector = self.compute_mean_vector(item["text"])
                if vector is None:
                    continue

                vec_list = vector.tolist()
                str_vec = " ".join([str(d) for d in vec_list])
                item_id = str(item["id"])
                result_list.append((item_id, str_vec))
            f.writelines('%d %d\n' % (len(result_list), self.get_dimension()))
            for (item_id, str_vec) in result_list:
                f.writelines('%s %s\n' % (item_id, str_vec))

    def preprocess_list_text(self, data_set):
        print("preprocess text")
        clean_data_set = []
        for item in data_set:
            try:
                item["text"] = item["text"].encode('utf-8')
                item["text"] = self.text_preprocessor.illegal_word_filter(item["text"])
                clean_data_set.append(item)
            except Exception:
                traceback.print_exc()
        print(clean_data_set)
        return clean_data_set

    def is_init_word2vec(self):
        if self.wv:
            return True
        else:
            return False

    def compute_similarity(self, vector1, vector2):
        return dot(matutils.unitvec(vector1), matutils.unitvec(vector2))

    def compute_mean_vector(self, text, need_process=False):
        if text is None or text.strip() == "":
            return None

        if need_process:
            text = self.text_preprocessor.illegal_word_filter(text)
        if self.is_init_word2vec() == False:
            return None
        words = text.split(" ")
        vector_dimension = self.get_dimension()
        valid_word_vec_list = []

        for word in words:
            new_word = word
            if new_word in self.vocab:
                vec = self.wv[new_word]
                valid_word_vec_list.append(vec)

        if len(valid_word_vec_list) > 0:
            return np.mean(valid_word_vec_list, axis=0)
        else:
            return np.zeros(vector_dimension)

    def get_dimension(self):
        if self.wv:
            return self.wv.vector_size
        else:
            return 0
