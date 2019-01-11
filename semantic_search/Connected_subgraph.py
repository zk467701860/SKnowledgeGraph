class Connected_subgraph:
    @staticmethod
    def Get_sub_maps(relation_list, node_list):
        res = []
        res_relation = []
        res_node = []
        for node in relation_list:
            flag = 0
            for i in range(0, len(res)):
                if node["start_id"] in res[i] or node["end_id"] in res[i]:
                    flag = 1
                    if node["start_id"] not in res[i]:
                        res[i].append(node["start_id"])
                    if node["end_id"] not in res[i]:
                        res[i].append(node["end_id"])
                    if node not in res_relation[i]:
                        res_relation[i].append(node)
                        for item in node_list:
                            if item["id"] == node["start_id"] or item["id"] == node["end_id"]:
                                res_node[i].append(item)
                                node_list.remove(item)
                    if len(res) > 1:
                        res, res_relation, res_node = Connected_subgraph.delete_compeat(res, res_relation, res_node)
                        break
            if not res or flag == 0:
                tmp = []
                tmp_relation = []
                tmp_node = []
                tmp.append(node["start_id"])
                tmp.append(node["end_id"])
                tmp_relation.append(node)
                res.append(tmp)
                res_relation.append(tmp_relation)
                for item in node_list:
                    if item["id"] == node["start_id"] or item["id"] == node["end_id"]:
                        tmp_node.append(item)
                        node_list.remove(item)
                res_node.append(tmp_node)
                # combine
                if len(res) > 1:
                    res, res_relation, res_node = Connected_subgraph.delete_compeat(res, res_relation, res_node)

        summary = []
        for relations, nodes in zip(res_relation, res_node):
            summary.append(
                {
                    "nodes": nodes,
                    "relations": relations,
                }
            )
        print("%%%%%%%%%%%%%%%%%%%")
        print res
        if node_list:
            summary.append(
                {
                    "nodes": node_list,
                    "relations": [],
                }
            )
        #return sorted(summary,key=lambda sum:len(sum["nodes"]))
        return summary

    @staticmethod
    def dic_list_delete_compeat(list1, list2):
        for item in list2:
            if item not in list1:
                list1.append(item)
        return list1

    @staticmethod
    def delete_compeat(res, res_relation, res_node):
        for index in range(0, len(res) - 1):
            for index2 in range(index + 1, len(res)):
                flag = 0
                for item in res[index]:
                    if item in res[index2]:
                        flag = 1
            if flag == 1:
                res[index] = Connected_subgraph.dic_list_delete_compeat(res[index], res[index2])
                res_relation[index] = Connected_subgraph.dic_list_delete_compeat(res_relation[index],
                                                                                 res_relation[index2])
                res_node[index] = Connected_subgraph.dic_list_delete_compeat(res_node[index], res_node[index2])
                res.pop(index2)
                res_relation.pop(index2)
                res_node.pop(index2)
                break
        return res, res_relation, res_node
