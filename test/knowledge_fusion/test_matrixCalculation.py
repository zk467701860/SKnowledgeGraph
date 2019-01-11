import numpy as np
from unittest import TestCase

from semantic_search.matrix_calculation import MatrixCalculation


class TestMatrixCalculation(TestCase):
    def test_get_most_similar_top_n_entity(self):
        sim_matrix=np.matrix(np.array([[1, 2, 3, 4],[6,6,1,5]]))
        one_hot_result= MatrixCalculation.get_most_similar_top_n_entity_as_matrix(top_n=3,s_e_similarity_matrix=sim_matrix)
        print(one_hot_result)
        one_hot_result = MatrixCalculation.get_most_similar_top_n_entity_as_matrix(top_n=5,
                                                                                   s_e_similarity_matrix=sim_matrix)
        print(one_hot_result)