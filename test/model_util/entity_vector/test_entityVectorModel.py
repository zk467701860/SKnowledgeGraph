from unittest import TestCase

from gensim import matutils
from numpy.core.multiarray import dot

from model_util.entity_vector.entity_vector_model import EntityVectorComputeModel, EntityVectorModel


class TestEntityVectorModel(TestCase):
    def test_compute_mean_vector(self):
        entity_vector_model = EntityVectorComputeModel()
        entity_vector_model.init_word2vec_model(path="vocab.test.plain.txt", binary=False)
        vector1 = entity_vector_model.compute_mean_vector("Public internet is very good")
        vector2 = entity_vector_model.compute_mean_vector("Public internet application is better than private")
        print(vector1)
        print(vector2)
        similarity = dot(matutils.unitvec(vector1), matutils.unitvec(vector2))
        print(similarity)

    def test_wiki_entity2vec_model(self):
        model = EntityVectorModel()
        wv = model.load("C:/Users/apple/PycharmProjects/newProject/SKnowledgeGraph/model_util/entity_vector/data/avg_word_vec/wikipedia.plain.txt")
        print(wv)
        print(wv["kg#84660"])

    def test_train_vector(self):
        #entity_vector_model = EntityVectorComputeModel()
        #entity_vector_model.init_word2vec_model(path="vocab.test.plain.txt", binary=False)
        #entity_vector_model.train_mean_vector("entity_description.json", "entity.vector.plain.txt")

        keyvector=EntityVectorModel.load("vocab.test.plain.txt",binary=False)
        print keyvector.vocab
        print "123" in keyvector.vocab
        vector1=keyvector["and"]
        vector2=keyvector["for"]
        print(vector1)
        print(vector2)
        similarity = dot(matutils.unitvec(vector1), matutils.unitvec(vector1))
        print(similarity)

        # print(keyvector.similarity("1","2"))
