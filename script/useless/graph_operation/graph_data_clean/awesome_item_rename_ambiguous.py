from skgraph.util.data_clean_util import construct_key_count_map


def awesome_item_rename_ambiguous(awesome_graph_accessor, node_collection):
    node_list = node_collection.get_all_nodes(1000, ['awesome item'])
    print len(node_list)

    node_map = construct_key_count_map(node_list)

    for key in node_map.keys():
        if len(node_map[key]) > 1:
            temp_node_list = node_map[key]
            print key
            for node in temp_node_list:
                if "url" in node:
                    url = node["url"]
                    parent_node = awesome_graph_accessor.find_start_by_relation_type_and_end_url("collect", url)
                    if parent_node is not None:
                        if "name" in parent_node:
                            node["name"] = node["name"] + " (" + parent_node["name"] + ")"
                    print node["name"]
                    awesome_graph_accessor.push_node(node)