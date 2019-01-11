import json
import multiprocessing
import random
from multiprocessing import Pool

import textdistance
from sklearn.cluster import AffinityPropagation

from model_util.entity_vector.entity_vector_model import EntityVectorModel


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


def calculate_similarity_matrix(selected_data_list, vector_map, weight, current_index, total_length):
    full_result = []
    lack_result = []
    if selected_data_list is not None:
        # print("there are total " + str(len(selected_data_list)) + " data.")
        for i in range(0, len(selected_data_list)):
            # print("execute the NO." + str(current_index) + " list now, there are total " + str(total_length) + " list.")
            # print("calculate the NO." + str(i) + " data's similarity, " + "there are total " + str(len(selected_data_list)) + " data.")
            first = str(selected_data_list[i]["paragraph_id"])
            first_noun_phrase = selected_data_list[i]["noun_phrase"]
            full_temp = []
            lack_temp = []
            for j in range(0, len(selected_data_list)):
                second = str(selected_data_list[j]["paragraph_id"])
                second_noun_phrase = selected_data_list[j]["noun_phrase"]
                if i == j:
                    similarity = 0
                else:
                    similarity = (vector_map.similarity(first, second) + 1) * weight / 2 + textdistance.jaccard(first_noun_phrase,
                                                                                                      second_noun_phrase) * (
                                         1 - weight)
                    similarity = round(similarity, 6) - 1
                    lack_temp.append(similarity)
                full_temp.append(similarity)
            full_result.append(full_temp)
            lack_result.append(lack_temp)
    return full_result, lack_result


def affinity_propagation(full_simi_matrix, lack_simi_matrix, data_list):
    p = -0.3  ##3 centers
    # p = np.min(lack_simi_matrix)  ##9 centers
    # p = np.median(lack_simi_matrix)  ##13 centers

    ap = AffinityPropagation(damping=0.5, max_iter=500, convergence_iter=30,
                             preference=p, affinity='precomputed').fit(full_simi_matrix)
    cluster_centers_indices = ap.cluster_centers_indices_
    labels = ap.labels_

    print("----------------------------------------")
    if cluster_centers_indices is not None:
        print(labels)
        print(cluster_centers_indices)
        for idx in cluster_centers_indices:
            print(data_list[idx])

        for i in range(0, len(cluster_centers_indices)):
            print(str(i) + "-----------------------------------")
            for j in range(0, len(labels)):
                if labels[j] == i:
                    print(data_list[j])
            print("\n")
        return labels, cluster_centers_indices


def generate_center_map(labels, cluster_centers_indices, data_list):
    result = []
    if labels is not None and cluster_centers_indices is not None and data_list is not None:
        for i in range(0, len(cluster_centers_indices)):
            center = data_list[cluster_centers_indices[i]]
            # index = center['id']
            paragraph_id = center['paragraph_id']
            noun_phrase = center['noun_phrase']
            merge_np_id = center['merge_np_id']
            sentence_id = center['sentence_id']
            sentence = center['sentence']
            sub_nodes = center['sub_nodes']
            for j in range(0, len(labels)):
                if labels[j] == i:
                    if len(data_list[j]['sub_nodes']) > 0:
                        sub_nodes.extend(data_list[j]['sub_nodes'])
                    temp_node = data_list[j]
                    temp_node['sub_nodes'] = []
                    sub_nodes.append(temp_node)
            temp = {"id": (i + 1), "sub_nodes": sub_nodes, "paragraph_id": paragraph_id, "noun_phrase": noun_phrase,
                    "merge_np_id": merge_np_id, "sentence_id": sentence_id, "sentence": sentence}
            result.append(temp)
    return result


def select_data_by_np_id(np_id_list, data_list):
    result = []
    if np_id_list is not None and data_list is not None:
        for each in data_list:
            merge_np_id = each["merge_np_id"]
            if merge_np_id in np_id_list and each not in result:
                result.append(each)
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


def update_data_list(data_list, vector_map):
    result = []
    length = len(data_list)
    for i in range(0, length):
        paragraph_id = data_list[i]["paragraph_id"]
        if str(paragraph_id) in vector_map.vocab:
            result.append(data_list[i])
    return result


def generate_total_np_id_list(data_list):
    result = []
    if data_list is not None:
        for each in data_list:
            result.append(each['merge_np_id'])
    return result


def write_in_file(filename, labels, cluster_centers_indices, data_list):
    if cluster_centers_indices is not None:
        with open(filename, 'w') as f:
            f.write("labels: " + str(labels.tolist()))
            f.write('\n')
            f.write("cluster_centers_indices: " + str(cluster_centers_indices.tolist()))
            f.write('\n')
            # for idx in cluster_centers_indices:
            #     f.write(data_list[idx])

            for i in range(0, len(cluster_centers_indices)):
                f.write(str(i) + "-----------------------------------\n")
                f.write("cluster center:\n")
                f.write(str(data_list[cluster_centers_indices[i]]))
                f.write('\n\n')

                for j in range(0, len(labels)):
                    if labels[j] == i:
                        f.write(str(data_list[j]))
                        f.write('\n')
                f.write('\n')


def single_process(i, total_np_id_list, data_list):
    print("execute the NO." + str(i) + " list now")
    np_id_list = total_np_id_list[i]
    print(len(np_id_list))
    total_length = len(total_np_id_list)
    print("total_length=" + str(total_length))

    # np_id_list = [50, 42424, 67]
    print("begin to select data list " + str(i))
    print(np_id_list)
    selected_data_list = select_data_by_np_id(np_id_list, data_list)
    print("select data list successfully")
    print("begin to update data list " + str(i))
    selected_data_list = update_data_list(selected_data_list, vector_map)
    processed_data_list = pre_process(selected_data_list)
    print("update data list successfully")
    print("begin to calculate similarity matrix...")
    full_simi_matrix, lack_simi_matrix = calculate_similarity_matrix(processed_data_list, vector_map, weight, i,
                                                                     total_length)
    print("calculate similarity matrix successfully")
    print("begin to run affinity propagation...")
    labels, cluster_centers_indices = affinity_propagation(full_simi_matrix, lack_simi_matrix,
                                                           processed_data_list)
    total_list = generate_center_map(labels, cluster_centers_indices, processed_data_list)
    # filename = "weight-" + str(weight) + "-result-" + str(i) + ".txt"
    # write_in_file(filename, labels, cluster_centers_indices, selected_data_list)
    print("the first round finish!")
    return total_list


if __name__ == "__main__":
    MAX_DEPTH = 20

    print("begin to load word2vec...")
    vector_map = load_word_to_vec()
    print("load word2vec successfully")
    # total_np_id_list = [[50, 42424, 67], [58129, 11680, 30]]
    weight_list = [0.5, 0.6, 0.7, 0.8, 0.9]
    for weight in weight_list:
        print("=======================================================")
        print("current weight is " + str(weight))
        print("begin to read data...")
        data_list, total_np_id_list = read_data()
        print("read data successfully")
        # total_np_id_list = [50, 42424, 67, 58129, 11680, 30]
        for depth in range(0, MAX_DEPTH):
            print("current depth is " + str(depth))
            total_list = []
            if depth == 0:
                limit = 500
            else:
                limit = 700
            if depth > 0:
                random.shuffle(total_np_id_list)  # add random factor
            total_np_id_list = [total_np_id_list[i: i + limit] for i in range(0, len(total_np_id_list), limit)]
            left_cpu = 4
            pool = Pool(processes=multiprocessing.cpu_count() - left_cpu)
            ret_lis = []
            for i in range(0, len(total_np_id_list)):
                # for i in range(0, 1):
                ret = pool.apply_async(single_process, args=(i, total_np_id_list, data_list))
                ret_lis.append(ret)
            pool.close()
            pool.join()
            for ret in ret_lis:
                total_list.extend(ret.get())

            total_np_id_list = generate_total_np_id_list(total_list)
            data_list = total_list
            result_filename = "weight-" + str(weight) + "-depth-" + str(depth) + ".json"
            with open(result_filename, 'w') as f:
                json.dump(total_list, f)
