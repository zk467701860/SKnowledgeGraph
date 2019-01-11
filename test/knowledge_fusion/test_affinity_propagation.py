from unittest import TestCase

import textdistance
from gensim import matutils
from numpy.core.multiarray import dot

from model_util.entity_vector.entity_vector_model import EntityVectorModel
from script.knowledgeFusion.affinity_propagation import pre_process


class TestAffinityPropagation(TestCase):
    def test_pre_process(self):
        data_list = [{"id": 1, "sentence_id": 1, "paragraph_id": 1, "sentence": "just a test sentence",
                    "merge_np_id": 1, "noun_phrase": "test", "sub_nodes": []},
                     {"id": 2, "sentence_id": 2, "paragraph_id": 2, "sentence": "just a test sentence",
                      "merge_np_id": 1, "noun_phrase": "test", "sub_nodes": []},
                     {"id": 3, "sentence_id": 3, "paragraph_id": 3, "sentence": "just a test sentence",
                      "merge_np_id": 3, "noun_phrase": "test2", "sub_nodes": []},
                     {"id": 4, "sentence_id": 4, "paragraph_id": 4, "sentence": "test case",
                      "merge_np_id": 4, "noun_phrase": "test4", "sub_nodes": []},
                     {"id": 5, "sentence_id": 5, "paragraph_id": 5, "sentence": "just a test sentence",
                      "merge_np_id": 3, "noun_phrase": "test5", "sub_nodes": []}]
        result = pre_process(data_list)
        for each in result:
            print(each)
            print(len(each["sub_nodes"]))

    def test_similarity_calculation(self):
        str1 = "AbstractInputMethodService provides a abstract base class for inut methods."
        str2 = "The default implementation in this abstract class returns 1.0 for all components."

        vector_map = EntityVectorModel.load("mean_vector_api_paragraph.plain.txt", binary=False)

        vector1 = vector_map.compute_mean_vector(str1)
        vector2 = vector_map.compute_mean_vector(str2)
        semantic_similarity = dot(matutils.unitvec(vector1), matutils.unitvec(vector2))
        print("semantic similarity is " + semantic_similarity)
        structure_similarity = textdistance.jaccard(str1, str2)
        print("structure similarity is " + structure_similarity)