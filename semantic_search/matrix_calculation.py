import numpy as np
from numpy.core.multiarray import dot


class MatrixCalculation:
    def __init__(self):
        pass

    @staticmethod
    def cosine_similarity(vec1, vec2):
        return float(np.sum(vec1 * vec2)) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    @staticmethod
    def matrix_mul(list_1, list_2):
        matrix_1 = np.array(list_1)
        matrix_2 = np.array(list_2)
        return dot(matrix_1, matrix_2)

    @staticmethod
    def cosine_matrix(list_1, list_2):
        matrix_1 = np.matrix(list_1)
        matrix_2 = np.matrix(list_2)
        matrix_mul = matrix_1 * matrix_2.transpose()
        norm_1 = np.sqrt(np.multiply(matrix_1, matrix_1).sum(axis=1))
        norm_2 = np.sqrt(np.multiply(matrix_2, matrix_2).sum(axis=1))
        return np.divide(matrix_mul, norm_1 * norm_2.transpose())

    @staticmethod
    def cosine_vec_to_matrix(vec, list_vec):
        return MatrixCalculation.cosine_matrix([vec, ], list_vec)

    @staticmethod
    def compute_cossin_for_vec_to_matrix_normalize(vector, list_vec):
        return (MatrixCalculation.cosine_vec_to_matrix(vector, list_vec) + 1) / 2

    @staticmethod
    def compute_cossin_for_matrix_to_matrix_normalize(list_1, list_2):
        return (MatrixCalculation.cosine_matrix(list_1, list_2) + 1) / 2

    @staticmethod
    def get_most_similar_top_n_entity_as_matrix(top_n, s_e_similarity_matrix):
        s_e_similarity_matrix_array = s_e_similarity_matrix.getA()
        # print("s_e_similarity_matrix_array", s_e_similarity_matrix_array)
        sentence_num = s_e_similarity_matrix_array.shape[0]

        entity_num = s_e_similarity_matrix_array.shape[1]
        if entity_num < top_n:
            one_hot_array = np.ones([sentence_num, entity_num])
        else:
            one_hot_array = np.zeros([sentence_num, entity_num])

            max_sim_index_2d_array = np.argsort(-s_e_similarity_matrix_array, axis=1)
            # print("max_sim_index_2d_array", max_sim_index_2d_array)
            for sentence_index, max_sim_index_array in enumerate(max_sim_index_2d_array):
                # print("sentence_index", sentence_index, "max_sim_index_array", max_sim_index_array)
                for entity_index in max_sim_index_array[:top_n]:
                    one_hot_array[sentence_index, entity_index] = 1
        # print("one_hot_array", one_hot_array)
        one_hot_matrix = np.matrix(one_hot_array)
        # print("np.matrix(one_hot_array)", one_hot_matrix)

        return one_hot_matrix

    @staticmethod
    def compute_cossin_for_one_to_one_in_two_list_normalize(list_1, list_2):
        return (MatrixCalculation.cosine_matrix_one_to_one_return_in_matrix(list_1, list_2) + 1) / 2

    @staticmethod
    def cosine_matrix_one_to_one_return_in_matrix(list_1, list_2):
        result_list = []
        for vec1, vec2 in zip(list_1, list_2):
            result_list.append(MatrixCalculation.cosine_similarity(vec1, vec2))
        return np.matrix([result_list])
