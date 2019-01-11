# encoding: utf-8
from gensim.models import KeyedVectors
import numpy as np
import sys
#import multiprocessing
#from multiprocessing import Process

average_distance = 3.4
'''
result_list = []
def compute(query_entity_list, sequence_list, begin, end, length, mydict):
    #print sequence_list
    minimal_entity_list = []
    minimal_distance = sys.maxint
    for i in range(begin, end):
        entity_list = []
        #print sequence_list[i]
        for j in range(0, length):
            #print query_entity_list[j]
            #print int(sequence_list[i][j])
            entity_list.append(query_entity_list[j][int(sequence_list[i][j])])
        distance = compute_distance_between_entities(entity_list, mydict)
        #print '%s  %s' % (entity_list, distance)
        if distance < minimal_distance:
            minimal_distance = distance
            minimal_entity_list = entity_list
    result_list.append([minimal_entity_list, minimal_distance])
            # entity_list form: [[],[],[]]

def get_final_entity_sequence_by_graph_embedding(query_entity_list):
    count = 0
    length = len(query_entity_list)
    #print query_entity_list
    for mention_entity in query_entity_list:
        count = count * 10 + len(mention_entity)
    sequence_list = generateAllSequence(str(count), length)
    mydict = multiprocessing.Manager().dict()
    mydict = KeyedVectors.load_word2vec_format('data/graph embedding/graph_output.emb', binary=False)
    if length > 6:
        total_pair = len(sequence_list)
        unit = total_pair / 5
        jobs = []
        for i in range(4):
            p = Process(target=compute, args=(query_entity_list,sequence_list, i * unit, (i + 1) * unit, length, mydict,))
            jobs.append(p)
            p.start()
        final_p = Process(target=compute, args=(query_entity_list, sequence_list, 4 * unit, total_pair, length, mydict,))
        jobs.append(final_p)
        final_p.start()
        for proc in jobs:
            proc.join()
    else:
        compute(query_entity_list, sequence_list, 0, len(sequence_list), length, mydict)
    if len(result_list) == 1:
        return result_list[0][0]
    else:
        minimal_entity_list = []
        minimal_distance = sys.maxint
        for result_pair in result_list:
            if result_pair[1] < minimal_distance:
                minimal_distance = result_pair[1]
                minimal_entity_list = result_pair[0]
        return minimal_entity_list

def generateAllSequence(word, num):
    res = []
    digit = int(word[len(word) - num])
    if num == 1:
        for i in range(0, digit):
            temp = str(i)
            res.append(temp)
        return res
    else:
        for i in range(0, digit):
            for string in generateAllSequence(word, num - 1):
                temp = str(i) + string
                res.append(temp)
        return res

def compute_distance_between_entities(entity_list, mydict):
    entity_vec = np.zeros(128)
    count = len(entity_list)
    distance = 0
    actual_point = 0
    #print entity_list
    for entity in entity_list:
        if entity == '-1':
            distance += average_distance
        else:
            vec = mydict[entity]
            # print vec
            entity_vec += np.array(vec)
            actual_point += 1
    if actual_point == 0:
        return float('inf')
    center_vec = entity_vec / actual_point
    # print center_vec
    for entity in entity_list:
        if entity != '-1':
            vec_array = np.array(mydict[entity])
            distance += np.linalg.norm(vec_array - center_vec)
    return distance / float(count)

'''
class GraphUtil:
    def __init__(self, path):
        self.wv = KeyedVectors.load_word2vec_format(path, binary=False)

    #entity_list form: [[],[],[]]
    def get_final_entity_sequence_by_graph_embedding(self, query_entity_list):
        minimal_entity_list = []
        minimal_distance = sys.maxint
        count = 0
        length = len(query_entity_list)
        for mention_entity in query_entity_list:
            count = count * 10 + len(mention_entity)
        sequence_list = self.generateAllSequence(str(count), length)
        for sequence in sequence_list:
            entity_list = []
            for i in range(0, length):
                entity_list.append(query_entity_list[i][int(sequence[i])])
            distance = self.compute_distance_between_entities(entity_list)
            #print '%s  %s' % (entity_list, distance)
            if distance < minimal_distance:
                minimal_distance = distance
                minimal_entity_list = entity_list
        return minimal_entity_list

    def generateAllSequence(self, word, num):
        res = []
        digit = int(word[len(word) - num])
        if num == 1:
            for i in range(0, digit):
                temp = str(i)
                res.append(temp)
            return res
        else:
            for i in range(0, digit):
                for string in self.generateAllSequence(word, num - 1):
                    temp = str(i) + string
                    res.append(temp)
            return res

    def compute_distance_between_entities(self, entity_list):
        entity_vec = np.zeros(128)
        count = len(entity_list)
        distance = 0
        actual_point = 0
        for entity in entity_list:
            if entity == '-1':
                distance += average_distance
            else:
                vec = self.wv[entity]
                #print vec
                entity_vec += np.array(vec)
                actual_point += 1
        if actual_point == 0:
            return float('inf')
        center_vec = entity_vec / actual_point
        #print center_vec
        for entity in entity_list:
            if entity != '-1':
                vec_array = np.array(self.wv[entity])
                distance += np.linalg.norm(vec_array - center_vec)
        return distance / float(count)

    def computeAverageTwoPointDistance(self):
        result = 0
        key_set = self.wv.vocab.keys()
        length = len(key_set)
        for i in range(0, length - 1):
            temp_result = 0
            for j in range(i + 1, length):
                temp_result += np.linalg.norm(np.array(self.wv[key_set[i]]) - np.array(self.wv[key_set[j]]))
            result += temp_result / (length - i - 1)
            print i
            print result
            print result / float(i + 1)
        return result / float(length - 1)


if __name__=="__main__":
    #graph = GraphUtil('data/graph embedding/graph_output.emb')
    #print np.linalg.norm(np.array(graph.wv['1845']) - np.array(graph.wv['1843']))
    #print np.linalg.norm(np.array(graph.wv['0']) - np.array(graph.wv['89924']))
    #print graph.compute_distance_between_entities(['975', '986'])
    #print graph.get_final_entity_sequence_by_graph_embedding([['1845'], ['1843']])
    test_list = []
    test_list.append(['-1','15903','19477','63180','19121'])
    test_list.append(['-1', '5873', '73435', '73496', '73449'])
    test_list.append(['-1', '1856', '6889', '26747', '975'])
    test_list.append(['-1', '18827', '18914'])
    test_list.append(['-1', '25229'])
    test_list.append(['-1', '72996', '73409', '73452', '73327'])
    test_list.append(['-1', '5244', '2184', '67159', '950'])
    test_list.append(['-1', '1040'])
    test_list.append(['-1', '73476', '1806', '1821', '1844'])
    test_list.append(['-1', '6764', '1414', '6086', '65915'])

    test_list.append(['-1', '72996', '73409', '73452', '73327'])
    print test_list
    a_list = []
    a_list.extend(test_list[0:5])
    print a_list
    a_list.extend(test_list[5:10])
    print a_list
    b_list = []
    b_list.append(['10'])
    print b_list
    b_list.append(['20'])
    print b_list
    #print get_final_entity_sequence_by_graph_embedding(test_list)
    #print graph.get_final_entity_sequence_by_graph_embedding([['321','-1','19208','1129','18199'],['321','-1','19208','1129','18199'],['7072','-1','7556','6253','1841'],['13039','-1','6170','7072','84761']])
    #print graph.get_final_entity_sequence_by_graph_embedding(test_list)
    #['19477', '73435', '975', '18827', '25229', '73452', '950', '1040', '73476', '1414', '73452']

    #print graph.get_final_entity_sequence_by_graph_embedding([['19477'], ['73435'], ['-1', '1856', '6889', '26747', '975'], ['18827', '-1'], ['25229','-1'], ['73452'], ['950'], ['1040'], ['73476'], ['1414'], ['73452']])
    #print graph.generateAllSequence('1234', 4)
    #print graph.computeAverageTwoPointDistance()