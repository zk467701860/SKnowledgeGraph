import json


def merge_awesome_nodes_from_file(awesome_graph_accessor):
    with open("duplicate_id_list.txt", 'r') as f:
        str_id_list = f.read()
        id_list = json.loads(str_id_list)

    print id_list

    for each in id_list:
        awesome_graph_accessor.merge_awesome_nodes(each)