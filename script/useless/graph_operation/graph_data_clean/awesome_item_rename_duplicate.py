import sys

reload(sys)
sys.setdefaultencoding('utf8')

from skgraph.graph.accessor.graph_accessor import GraphAccessor, DefaultGraphAccessor
from skgraph.util.data_clean_util import get_name_by_github_url, construct_key_count_map, url_similarity, \
    description_similarity, property_in_dict_list, rename_property


def awesome_item_rename_duplicate(awesome_graph_accessor, node_collection):
    node_list = node_collection.get_all_nodes(1000, ['awesome item'])
    print len(node_list)

    node_map = construct_key_count_map(node_list)

    i = 0
    for key in node_map.keys():
        if len(node_map[key]) > 1:
            print key, " ", len(node_map[key])
            for each in node_map[key]:
                print each
            i += 1
    print i

    node_list_after_step1 = []
    for key in node_map.keys():
        if len(node_map[key]) > 1:
            step1_node_list = node_map[key]
            for node in step1_node_list:
                if "url" in dict(node):
                    url = node["url"]
                    if "//github.com/" in url:
                        # print url, " ", type(url)
                        github_name = get_name_by_github_url(url)
                        if github_name != "" and github_name.lower() != key.lower():
                            node["name"] = github_name
                        node_list_after_step1.append(node)
                    else:
                        node_list_after_step1.append(node)
                else:
                    node_list_after_step1.append(node)

    for node in node_list_after_step1:
        print node
        awesome_graph_accessor.push_node(node)

    node_map_after_step1 = construct_key_count_map(node_list_after_step1)

    # i = 0
    # for key in node_map_after_step1.keys():
    #     if len(node_map_after_step1[key]) > 1:
    #         print key, " ", len(node_map_after_step1[key]), " ", node_map_after_step1[key]
    #         i += 1
    # print i

    # with open("node_map_after_step1.txt", 'w') as f:
    #     for key in node_map_after_step1.keys():
    #         if len(node_map_after_step1[key]) > 1:
    #             nodes_str = key + " " + str(len(node_map_after_step1[key])) + " " + str(node_map_after_step1[key])
    #             f.write(nodes_str + "\n")z

    node_list_after_step2 = []
    for key in node_map_after_step1.keys():
        step2_node_list = node_map_after_step1[key]
        for i in range(0, len(step2_node_list) - 1):
            for j in range(i + 1, len(step2_node_list)):
                if "url" in step2_node_list[i]:
                    url1 = step2_node_list[i]["url"]
                else:
                    url1 = ""

                if "url" in step2_node_list[j]:
                    url2 = step2_node_list[j]["url"]
                else:
                    url2 = ""

                if "description" in step2_node_list[i]:
                    description1 = step2_node_list[i]["description"]
                else:
                    description1 = ""

                if "description" in step2_node_list[j]:
                    description2 = step2_node_list[j]["description"]
                else:
                    description2 = ""

                if description1 != "" and description2 != "":
                    desc_sim = description_similarity(description1, description2)
                    if desc_sim >= 0.7:
                        step2_node_list[i].setdefault("duplicate", 1)
                        step2_node_list[j].setdefault("duplicate", 1)
                else:
                    url_sim = 0
                    if url1 != "" and url2 != "":
                        url_sim = url_similarity(url1, url2)
                    if url_sim >= 0.8:
                        step2_node_list[i].setdefault("duplicate", 2)
                        step2_node_list[j].setdefault("duplicate", 2)
                    else:
                        node1 = awesome_graph_accessor.find_start_by_relation_type_and_end_url("collect", url1)
                        node2 = awesome_graph_accessor.find_start_by_relation_type_and_end_url("collect", url2)
                        if node1 is not None and node2 is not None:
                            node_id1 = GraphAccessor.get_id_for_node(node1)
                            node_id2 = GraphAccessor.get_id_for_node(node2)
                            if node_id1 == node_id2:
                                step2_node_list[i].setdefault("duplicate", 3)
                                step2_node_list[j].setdefault("duplicate", 3)

        for each in step2_node_list:
            node_list_after_step2.append(each)

    node_map_after_step2 = construct_key_count_map(node_list_after_step2)
    # i = 0
    # for key in node_map_after_step2.keys():
    #     if len(node_map_after_step2[key]) > 1 and property_in_dict_list("duplicate", node_map_after_step2[key]) is True:
    #         print key, " ", len(node_map_after_step2[key]), " ", node_map_after_step2[key]
    #         i += 1
    # print i

    pending_map = {}
    duplicate_id_list = []
    for key in node_map_after_step2.keys():
        temp_list = []
        temp_id_list = []
        if len(node_map_after_step2[key]) > 1 and property_in_dict_list("duplicate", node_map_after_step2[key]) is True:
            for each in node_map_after_step2[key]:
                if "duplicate" in dict(each):
                    temp_list.append(each)
                    temp_id_list.append(DefaultGraphAccessor.get_id_for_node(each))
            pending_map.setdefault(key, temp_list)
            duplicate_id_list.append(temp_id_list)

    for key in pending_map.keys():
        pending_list = rename_property(pending_map[key])
        for each in pending_list:
            print each
            awesome_graph_accessor.push_node(each)
    print len(pending_map)

    with open("duplicate_id_list.txt", 'w') as f:
        f.write(str(duplicate_id_list))


