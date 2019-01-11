from skgraph.util.data_clean_util import construct_key_count_map


def merge_awesome_nodes_from_database(awesome_graph_accessor, node_collection):
    node_list = node_collection.get_all_nodes(1000, ['awesome item'])
    print len(node_list)

    node_map = construct_key_count_map(node_list)

    duplicate_id_map = {}
    for key in node_map.keys():
        if len(node_map[key]) > 1:
            print key
            temp_node_list = node_map[key]
            print len(temp_node_list), " ", temp_node_list
            for i in range(0, len(temp_node_list) - 1):
                for j in range(i + 1, len(temp_node_list)):
                    if "url" in temp_node_list[i] and "url" in temp_node_list[j]:
                        url1 = temp_node_list[i]["url"]
                        url2 = temp_node_list[j]["url"]
                        id1 = awesome_graph_accessor.get_id_for_node(temp_node_list[i])
                        id2 = awesome_graph_accessor.get_id_for_node(temp_node_list[j])
                        print url1, " ", url2
                        node1 = awesome_graph_accessor.find_start_by_relation_type_and_end_url("collect", url1)
                        node2 = awesome_graph_accessor.find_start_by_relation_type_and_end_url("collect", url2)
                        if node1 is not None and node2 is not None:
                            node_id1 = awesome_graph_accessor.get_id_for_node(node1)
                            node_id2 = awesome_graph_accessor.get_id_for_node(node2)
                            if node_id1 == node_id2:
                                new_key = key + " (" + node1["name"] + ")"
                                if new_key in duplicate_id_map:
                                    temp_id_list = duplicate_id_map[new_key]
                                    if id1 not in temp_id_list:
                                        temp_id_list.append(id1)
                                    if id2 not in temp_id_list:
                                        temp_id_list.append(id2)
                                else:
                                    duplicate_id_map.setdefault(new_key, [id1, id2])
    for key in duplicate_id_map:
        print key, " ", duplicate_id_map[key]
        awesome_graph_accessor.merge_awesome_nodes(duplicate_id_map[key])