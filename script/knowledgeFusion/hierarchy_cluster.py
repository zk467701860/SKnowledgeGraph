import json
from scipy.cluster.hierarchy import fcluster

import numpy as np

from script.knowledgeFusion.get_linkage_data import get_cluster_indices


def read_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data


def hierarchy_cluster(Z, threshold=0.2):
    cluster_assignments = fcluster(Z, threshold, criterion='distance')
    num_clusters = cluster_assignments.max()
    indices = get_cluster_indices(cluster_assignments)
    return num_clusters, indices


def construct_result_list(indices, data_list):
    result = []
    for k, ind in enumerate(indices):
        cluster_center = data_list[ind[0]]
        for j in range(1, len(ind)):
            if len(data_list[ind[j]]["sub_nodes"]) > 0:
                cluster_center["sub_nodes"].extend(data_list[ind[j]]["sub_nodes"])
            temp = data_list[ind[j]]
            temp["sub_nodes"] = []
            cluster_center["sub_nodes"].append(temp)
        result.append(cluster_center)
    for each in result:
        print(each)
    return result


def start_hierarchy_cluster():
    threshold_list = [0.6,0.8,1.0,1.2,1.4,1.6,1.8,2]
    linkage_filename = "linkage_result.json"
    linkage_data = read_data(linkage_filename)
    data_list_filename = "data_list.json"
    data_list = read_data(data_list_filename)
    if len(linkage_data) == len(data_list):
        for threshold in threshold_list:
            filename = 'threshold-' + str(threshold) + '-hierarchy_cluster.json'
            print("run threshold " + str(threshold) + " hierarchy cluster")
            with open(filename, 'w') as f:
                total_result = []
                for i in range(0, len(linkage_data)):
                    Z = np.array(linkage_data[i])
                    selected_data_list = data_list[i]
                    num_clusters, indices = hierarchy_cluster(Z, threshold)
                    result = construct_result_list(indices, selected_data_list)
                    total_result.extend(result)
                json.dump(total_result, f)


if __name__ == "__main__":
    start_hierarchy_cluster()
