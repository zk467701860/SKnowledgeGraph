# -*- coding:utf8 -*-
# from graph.graph_util.question_answer_system.graph.graph_client import GraphClient
import copy

max_iterator = 6
file_name = 'data.ppi'


class DataCreateUtil:
    def __init__(self, client):
        self.client = client

    def createData(self, begin_point_index):
        '''
        '''
        edge_dict = {}
        # file_name = 'data_' + str(begin_point_index) + '.ppi'
        file = open(file_name, 'w')
        iterator = 1
        id_list = []
        id_list.append(begin_point_index)
        total_id_list = []
        # len_list = []
        total_id_list.extend(id_list)
        while iterator <= max_iterator:
            temp_id_list = []
            # len_list.append(len(id_list))
            old_edge_dict = copy.deepcopy(edge_dict)
            old_total_id_list = copy.deepcopy(total_id_list)
            for id in id_list:
                nodes = self.client.get_adjacent_node_id_list(id)
                # print nodes
                if nodes == [] and iterator == 1:
                    return 0
                # print 'id  : %d  list : %s  length : %d ' % (id, nodes, len(nodes))
                for node in nodes:
                    if id not in edge_dict:
                        edge_dict[id] = [node]
                    else:
                        temp_list = edge_dict[id]
                        temp_list.append(node)
                        edge_dict[id] = temp_list
                    if node not in edge_dict:
                        edge_dict[node] = [id]
                    else:
                        temp_list = edge_dict[node]
                        temp_list.append(id)
                        edge_dict[node] = temp_list
                        # file.writelines("%d\t%d\t%.4f\n"%(id, node, 1 / float(len(nodes))))
                # file.flush()
                temp_id_list.extend(nodes)
            # calculate current edge number
            total_edge_number = 0
            for key in edge_dict.keys():
                weight_edge_dict = {}
                temp_edge_list = edge_dict[key]
                for i in range(0, len(temp_edge_list)):
                    if temp_edge_list[i] not in weight_edge_dict:
                        weight_edge_dict[temp_edge_list[i]] = 1
                    else:
                        weight_edge_dict[temp_edge_list[i]] += 1
                total_edge_number += len(weight_edge_dict)
            # print 'iterator: %d  ,edge number: %d' %(iterator, total_edge_number)
            if len(set(total_id_list)) + len(set(temp_id_list)) < 10000:
                id_list = []
                id_list.extend(temp_id_list)
                total_id_list.extend(id_list)
            else:
                edge_dict = copy.deepcopy(old_edge_dict)
                id_list = []
                break
            if total_edge_number > 8000:
                edge_dict = copy.deepcopy(old_edge_dict)
                total_id_list = copy.deepcopy(old_total_id_list)
                id_list = []
                break
            if iterator < max_iterator and total_edge_number > 4000:
                total_id_list.extend(temp_id_list)
                id_list = []
                break
            if id_list == []:
                break
            # print 'id list : %s ' % (id_list)
            # print 'id list length: %d ' % (len(set(total_id_list)))
            # print 'iterator %d end' % (iterator)
            iterator += 1
            # print id_list
        if len(id_list) != 0:
            total_id_list.extend(id_list)
        print 'iterator: %d  ,edge number: %d' % (iterator, total_edge_number)
        print 'id: %d,   id list length: %d ' % (begin_point_index, len(set(total_id_list)))
        # for key in edge_dict.keys():
        # print key, ":", edge_dict[key]
        # calculate edge weight between two directed node with adding opposite edge

        for key in edge_dict.keys():
            weight_edge_dict = {}
            temp_edge_list = edge_dict[key]
            for i in range(0, len(temp_edge_list)):
                if temp_edge_list[i] not in weight_edge_dict:
                    weight_edge_dict[temp_edge_list[i]] = 1
                else:
                    weight_edge_dict[temp_edge_list[i]] += 1
            for count_key in weight_edge_dict.keys():
                file.writelines(
                    "%d\t%d\t%.4f\n" % (key, count_key, weight_edge_dict[count_key] / float(len(temp_edge_list))))
                file.flush()
        # total_id_set = set(total_id_list)
        # print len_list
        # print total_id_list
        # print len(total_id_list)
        # print len(total_id_set)
        file.close()
        return 1

        # if __name__ == '__main__':
        # client_1 = GraphClient()
        # system = DataCreateUtil(client_1)
        # system.createData(428)
