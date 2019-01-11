import MySQLdb

conn = MySQLdb.connect(
    host='10.141.221.75',
    port=3306,
    user='root',
    passwd='root',
    db='graphApplication',
    charset='utf8'
)
cur = conn.cursor()


class SimilarityGenerator:
    def __init__(self):
        self.cache_dict = {}
        # def __init__(self, client_1, max_id):
        # self.client_1 = client_1
        # self.max_id = max_id

        # compare two node list similarity with connection count and simple path

    def compareSimilarity_with_sumAndPath(self, list_1, list_2):
        total = 0
        for begin_id in list_1:
            # begin node is existed  # end node is existed
            for end_id in list_2:
                if begin_id == end_id:
                    total += 2
                else:
                    temp_count = self.get_connection_count_between_node(begin_id, end_id)
                    total += temp_count
                    if temp_count == 0:
                        total += self.compareNodeSimilarity_with_simple_path(begin_id, end_id)
                    temp_count = self.get_connection_count_between_node(end_id, begin_id)
                    total += temp_count
                    if temp_count == 0:
                        total += self.compareNodeSimilarity_with_simple_path(end_id, begin_id)
        return total

        # compare two node list similarity with connection count and simple path

    def compareSimilarity_with_sum(self, compare_post_json, list_1, list_2):
        total = 0
        api_json_list = []
        big_than_zero = 0
        for begin_id in list_1:
            # begin node is existed  # end node is existed
            for end_id in list_2:
                api_json_item = {}
                api_json_item['entity_id_1'] = begin_id
                api_json_item['entity_id_2'] = end_id
                api_json_item['RWR count'] = 0
                if begin_id == end_id:
                    # print '%d    %d    %f' % (begin_id, end_id, 1)
                    api_json_item['RWR count'] = 1
                    total += 2
                    api_json_list.append(api_json_item)
                    big_than_zero += 1
                    '''
                    api_json_item = {}
                    api_json_item['entity_id_1'] = end_id
                    api_json_item['entity_id_2'] = begin_id
                    api_json_item['RWR count'] = 1
                    api_json_list.append(api_json_item)
                '''
                else:
                    find_key = str(begin_id) + '&' + str(end_id)
                    if find_key in self.cache_dict:
                        temp_count = self.cache_dict[find_key]
                    else:
                        temp_count = self.get_connection_count_between_node(begin_id, end_id)
                        if len(self.cache_dict) < 10000:
                            self.cache_dict[find_key] = temp_count
                        else:
                            self.cache_dict.popitem()
                            self.cache_dict[find_key] = temp_count
                    # print '%d    %d    %f' % (begin_id, end_id, temp_count)
                    '''
                    if temp_count > 0.00000001:
                        big_than_zero += 1
                        total += temp_count
                        print '%d    %d    %f' % (begin_id, end_id, temp_count)
                        api_json_item['RWR count'] = temp_count
                        api_json_list.append(api_json_item)'''
                    total += temp_count
                    # print '%d    %d    %f' % (begin_id, end_id, temp_count)
                    api_json_item['RWR count'] = temp_count
                    api_json_list.append(api_json_item)

                    api_json_item = {}
                    api_json_item['entity_id_1'] = end_id
                    api_json_item['entity_id_2'] = begin_id
                    api_json_item['RWR count'] = 0
                    find_key = str(end_id) + '&' + str(begin_id)
                    if find_key in self.cache_dict:
                        temp_count = self.cache_dict[find_key]
                    else:
                        temp_count = self.get_connection_count_between_node(end_id, begin_id)
                        if len(self.cache_dict) < 10000:
                            self.cache_dict[find_key] = temp_count
                        else:
                            self.cache_dict.popitem()
                            self.cache_dict[find_key] = temp_count
                    # print '%d    %d    %f' % (end_id, begin_id, temp_count)
                    api_json_item['RWR count'] = temp_count
                    api_json_list.append(api_json_item)
                    total += temp_count

        compare_post_json['api_entity_relevance'] = api_json_list
        return total, big_than_zero

    '''
    future work 
    # compare two node list similarity with converting list to the vector of the count of getting to other node, and calculate cosine similarity of two vector
    def compareSimilarity_with_cosine(self, list_1, list_2):
        vector_1 = self.construct_vector_from_node_list(list_1)
        vector_2 = self.construct_vector_from_node_list(list_2)
        print 'begin array'
        array_1 = numpy.array(vector_1)
        array_2 = numpy.array(vector_2)
        print 'begin num'
        num = numpy.squeeze(numpy.dot(array_1, numpy.transpose([array_2])))
        print 'begin denom'
        denom = numpy.linalg.norm(array_1) * numpy.linalg.norm(array_2)
        cos = num / denom
        similarity = 0.5 + 0.5 * cos
        return similarity
    
    def construct_vector_from_node_list(self, node_list):
        vector = []
        print 'begin construct'
        for id in range(1, max_id + 1):
            if self.client_2.find_node_by_link_id(id) != None:
                print id
                score = 0
                list_length = len(node_list)
                for i in range(0, list_length):
                    if self.client_2.find_node_by_link_id(node_list[i]) != None:
                        temp_result = self.client_2.get_connection_count_between_node(node_list[i], id)
                        #print '%d  %d  %s' %(id, i, temp_result)
                        if temp_result != None:
                            score += temp_result
                vector.append(score)
            else:
                vector.append(0)
        return vector
    '''

    # compare two node similarity with path according to transition probability
    def compareNodeSimilarity_with_simple_path(self, node_1, node_2):
        total = 0
        threshold = 3
        adjacent_dict = {}
        iterator = 0
        id_list = []
        id_list.append(node_1)
        while iterator < threshold:
            temp_id_list = []
            for current_id in id_list:
                id_next_list = self.client_1.get_adjacent_node_id_list(current_id)
                if id_next_list == []:
                    if iterator == 0:
                        return 0
                    else:
                        continue
                for next_id in id_next_list:
                    if iterator > 0:
                        if next_id in adjacent_dict:
                            adjacent_dict[next_id] += self.get_connection_count_between_node(current_id, next_id) * \
                                                      adjacent_dict[current_id]
                        else:
                            adjacent_dict[next_id] = self.get_connection_count_between_node(current_id, next_id) * \
                                                     adjacent_dict[current_id]
                    else:
                        if next_id in adjacent_dict:
                            adjacent_dict[next_id] += self.get_connection_count_between_node(current_id, next_id)
                        else:
                            adjacent_dict[next_id] = self.get_connection_count_between_node(current_id, next_id)
                            # print '%d\t%d\t%.12f' % (current_id, next_id, adjacent_dict[next_id])
                temp_id_list.extend(id_next_list)
            id_list = []
            id_list.extend(temp_id_list)
            iterator += 1
        if node_2 in adjacent_dict:
            total += adjacent_dict[node_2]
        # print 'simple path %d to %d  count is : %f' %(node_1, node_2, total)
        return total

    # search count between two node
    def get_connection_count_between_node(self, begin_id, end_id):
        count = 0
        count += self.get_connection_count_by_mysql(begin_id, end_id)
        # count += self.get_connection_count_by_mysql(end_id, begin_id)
        # print '%d to %d  count is : %f' %(begin_id, end_id, count)
        return count

    # search count of id > 92354
    def get_connection_count_by_mysql(self, begin_id, end_id):
        count = 0
        # print "%d %d" %(begin_id,end_id)
        try:
            cur.execute('select count from randomWalkCount where startID = %s and endID = %s', (begin_id, end_id))
            counts = cur.fetchone()
            # print counts
            if counts != None:
                count = counts[0]
            # cur.close()
            # print count
            return count
        except MySQLdb.Error, e:
            print 'Mysql connection Error %d: %s' % (e.args[0], e.args[1])

    '''
    #search count of id <= 92354
    def get_connection_count_by_neo4j(self, begin_id, end_id):
        count = 0
        if self.client_2.find_node_by_link_id(begin_id) != None and self.client_2.find_node_by_link_id(end_id) != None:
            temp_result = self.client_2.get_connection_count_between_node(begin_id, end_id)
            if temp_result != None:
                count += temp_result
        return count
    '''

    # close mysql connect
    def close_mysql(self):
        try:
            conn.close()
        except MySQLdb.Error, e:
            print 'Mysql close Error %d: %s' % (e.args[0], e.args[1])


if __name__ == '__main__':
    # client = DefaultGraphAccessor(GraphClient(server_number=1))
    # max_id = client_1.get_max_id_for_node()
    # print max_id
    # generator = SimilarityGenerator(client_1, max_id)
    list_1 = [32844]
    list_2 = [59841]
    # print generator.compareSimilarity_with_sumAndPath(list_1, list_2)
    # generator.close_mysql()
