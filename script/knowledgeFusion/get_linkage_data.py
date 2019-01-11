import json
import multiprocessing
import traceback
from multiprocessing import Pool

import numpy as np
import textdistance
from scipy.cluster.hierarchy import linkage

from model_util.entity_vector.entity_vector_model import EntityVectorModel
from semantic_search.matrix_calculation import MatrixCalculation


def read_data():
    result = []
    np_id_list = []
    with open("np_data.json", 'r') as f:
        data_json_list = json.load(f)
    index = 0
    for each in data_json_list:
        paragraph_id_list = each["paragraph_id_list"]
        sentence_id_list = each["sentence_id_list"]
        sentence_list = each["sentence_list"]
        np_id_list.append(each["merge_np_id"])
        for i in range(0, len(paragraph_id_list)):
            sentence_id = sentence_id_list[i]
            paragraph_id = paragraph_id_list[i]
            sentence = sentence_list[i]
            merge_np_id = each["merge_np_id"]
            noun_phrase = each["noun_phrase"]
            temp = {"id": index, "sentence_id": sentence_id, "paragraph_id": paragraph_id, "sentence": sentence,
                    "merge_np_id": merge_np_id, "noun_phrase": noun_phrase, "sub_nodes": []}
            result.append(temp)
            index += 1
    return result, np_id_list


def load_word_to_vec():
    return EntityVectorModel.load("mean_vector_api_paragraph.plain.txt", binary=False)


def select_data_by_np_id(np_id_list, data_list):
    result = []
    if np_id_list is not None and data_list is not None:
        for each in data_list:
            merge_np_id = each["merge_np_id"]
            if merge_np_id in np_id_list and each not in result:
                result.append(each)
    return result


def update_data_list(data_list, vector_map):
    result = []
    length = len(data_list)
    for i in range(0, length):
        paragraph_id = data_list[i]["paragraph_id"]
        if str(paragraph_id) in vector_map.vocab:
            result.append(data_list[i])
    return result


def pre_process(data_list):
    result = []
    temp_sentence_list = []
    if data_list is not None:
        for i in range(0, len(data_list)):
            sentence_1 = data_list[i]["sentence"] + " " + str(data_list[i]["merge_np_id"])
            if sentence_1 not in temp_sentence_list:
                temp_sentence_list.append(sentence_1)
                temp_1 = data_list[i]
                for j in range(i, len(data_list)):
                    sentence_2 = data_list[j]["sentence"] + " " + str(data_list[j]["merge_np_id"])
                    if sentence_2 == sentence_1 and data_list[j]["merge_np_id"] == data_list[i][
                        "merge_np_id"] and i != j:
                        if len(data_list[j]["sub_nodes"]) > 0:
                            temp_1["sub_nodes"].extend(data_list[j]["sub_nodes"])
                        temp_2 = data_list[j]
                        temp_2["sub_nodes"] = []
                        temp_1["sub_nodes"].append(temp_2)
                result.append(temp_1)
    return result


def calculate_matrix(selected_data_list, vector_map):
    vector_list = []
    for i in range(0, len(selected_data_list)):
        paragraph_id = str(selected_data_list[i]["paragraph_id"])
        vector = vector_map[paragraph_id]
        vector_list.append(vector)
    return MatrixCalculation.cosine_matrix(vector_list, vector_list)


def calculate_similarity_matrix(selected_data_list, vector_map, weight):
    full_result = []
    id_list = []
    if selected_data_list is not None:
        vector_matrix = calculate_matrix(selected_data_list, vector_map).tolist()
        for i in range(0, len(selected_data_list)):
            first_noun_phrase = selected_data_list[i]["noun_phrase"]
            id_list.append(selected_data_list[i]["id"])
            full_temp = []
            for j in range(0, len(selected_data_list)):
                second_noun_phrase = selected_data_list[j]["noun_phrase"]
                if i == j:
                    similarity = 0
                else:
                    similarity = (vector_matrix[i][j] + 1) * weight / 2 + textdistance.jaccard(
                        first_noun_phrase,
                        second_noun_phrase) * (
                                         1 - weight)
                    similarity = -round(similarity, 6) + 1
                full_temp.append(similarity)
            full_result.append(full_temp)
    return full_result, id_list


def symmetry_matrix(data):
    if data is not None:
        r, c = data.shape
        for i in xrange(r):
            for j in xrange(i, c):
                if data[i][j] != data[j][i]:
                    data[i][j] = data[j][i]
    return data


def hierarchy_cluster(data, method='average'):
    data = np.array(data)
    Z = linkage(data, method=method)
    # print(Z)
    return Z


def get_cluster_indices(cluster_assignments):
    n = cluster_assignments.max()
    indices = []
    for cluster_number in range(1, n + 1):
        indices.append(np.where(cluster_assignments == cluster_number)[0])
    return indices


def single_process(i, total_np_id_list, data_list, vector_map):
    print("execute the NO." + str(i) + " list now")
    np_id_list = total_np_id_list[i]
    print(len(np_id_list))
    print("begin to select data list " + str(i))
    print(np_id_list)
    selected_data_list = select_data_by_np_id(np_id_list, data_list)
    print("select data list successfully")
    print("begin to update data list " + str(i))
    selected_data_list = pre_process(selected_data_list)
    selected_data_list = update_data_list(selected_data_list, vector_map)
    print("update data list successfully")
    print("begin to calculate similarity matrix")
    similarity_matrix, id_list = calculate_similarity_matrix(selected_data_list, vector_map, weight=0.5)
    # for each in similarity_matrix:
    #     print(each)
    # print(similarity_matrix)
    print("calculate similarity matrix successfully")
    data = np.array(similarity_matrix)
    print("begin to symmetry matrix")
    data = symmetry_matrix(data)
    print("symmetry matrix successfully")
    print("begin to run hierarchy cluster")
    Z = hierarchy_cluster(data)
    print("run hierarchy cluster successfully")
    return (Z, selected_data_list)


def start_get_linkage_data():
    limit = 500
    print("begin to load word2vec...")
    vector_map = load_word_to_vec()
    print("load word2vec successfully")
    data_list, total_np_id_list = read_data()
    # data_list = pre_process(data_list)
    total_np_id_list = [total_np_id_list[i: i + limit] for i in range(0, len(total_np_id_list), limit)]
    # total_np_id_list = [[50, 42424, 67, 58129, 11680, 30]]
    left_cpu = 2
    pool = Pool(processes=multiprocessing.cpu_count() - left_cpu)
    ret_list = []
    for i in range(0, len(total_np_id_list)):
        ret = pool.apply_async(single_process, args=(i, total_np_id_list, data_list, vector_map))
        ret_list.append(ret)
        # ret_list2.append(ret2)
        # single_process(i, total_np_id_list, data_list, vector_map)
    pool.close()
    pool.join()
    total_result = []
    total_data_list = []
    for index, ret in enumerate(ret_list):
        try:
            total_result.append(ret.get()[0].tolist())
            total_data_list.append(ret.get()[1])
        except:
            traceback.print_exc()
            print("error happen in %d", index)
    result_filename = "linkage_result.json"
    with open(result_filename, 'w') as f:
        json.dump(total_result, f)
    data_list_filename = "data_list.json"
    with open(data_list_filename, 'w') as f:
        json.dump(total_data_list, f)


if __name__ == "__main__":
    start_get_linkage_data()
