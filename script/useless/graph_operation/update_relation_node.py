from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient

client = DefaultGraphAccessor(GraphClient(server_number=1))
relation_type_list = client.get_all_relation_type()
for relation_name in relation_type_list:
    client.create_relation_node(relation_name=relation_name)
label_list = client.get_all_label_list()
remove_lables = ["wall", "wikidata", "wd_property", "relation", "schema"]
for label in label_list:
    if label not in remove_lables:
        node = client.find_a_node_by_label(label)
        if node is not None:
            for property in node.keys():
                client.create_relation_node(relation_name=property)
