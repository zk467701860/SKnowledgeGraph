# encoding: utf-8
import json
from GraphEmbeddingUtil import GraphUtil

def method1():
    graph = GraphUtil('data/graph embedding/graph_output.emb')
    # test paragraph
    # file = open('data/fel evaluation/step1-paragraph-test-new.txt', 'w')

    # test post
    result_file = open('data/fel evaluation/step3-post-test-v3.txt', 'w')

    id_entity_dict = {}
    with open('data/id-entity.tsv', 'r') as load_f:
        for line in load_f:
            content = line.split('\t')
            id_entity_dict[content[1].replace('\n', '')] = content[0]

    total = 0
    test_file = open('data/fel evaluation/batchset-9.json', 'r')
    post_list = json.load(test_file)
    for post in post_list:
        total += len(post['alias_entity'])

    TP = 0
    total_recognize = 0
    total_link = 0
    FN = 0
    with open('data/fel evaluation/predict-40-5-0.json', 'r') as load_f:
        load_dict = json.load(load_f)
        print 'total post number:  %d' % (len(load_dict))
        result_file.writelines('total lines is : %d\n' % (len(load_dict)))
        # print 'total lines is : %d' % (len(load_dict))
        # 每个帖子
        for i in range(0, len(load_dict)):
            pair_list = load_dict[i]['mention_entity']
            print i + 1
            result_file.writelines('current_line_index : %d,  post id : %s,  user labelled: %d\n' % (
                i + 1, post_list[i]['id'], len(post_list[i]['alias_entity'])))
            # print len(pair_list)
            total_recognize += len(pair_list)
            needMatch = []
            match_dict = {}
            match_index = 0
            for pair in post_list[i]['alias_entity']:
                needMatch.append((pair['begin_index'], pair['end_index']))
                match_dict[match_index] = False
                match_index += 1
            input_step3_list = []
            input_step3_mention_index = []
            # print needMatch
            # 每个识别出的mention集合
            recoginze_index = -1
            proportion_list = []
            for rec_pair in pair_list:
                temp_set = set()
                for inner_pair in rec_pair:
                    temp_set.add((inner_pair['begin'], inner_pair['end']))

                # print temp_set
                # 匹配当前list中是否有用户标记的mention
                match_mention_index = 0
                isMatch = False
                for need_match_pair in needMatch:
                    if match_dict[match_mention_index] == False:
                        if temp_set.isdisjoint(set([need_match_pair])) == False:
                            isMatch = True
                            match_dict[match_mention_index] == True
                            match_index -= 1
                            break
                    match_mention_index += 1

                '''
                if rec_pair[0]['id'] != -1:
                    temp_list = []
                    proportion = rec_pair[0]['score'] / (rec_pair[0]['score'] + rec_pair[1]['score'])
                    for inner_pair in rec_pair:
                        temp_list.append(str(inner_pair['id']))
                    input_step3_list.append(temp_list)
                    if isMatch:
                        proportion_list.append((proportion, match_mention_index))
                        input_step3_mention_index.append(match_mention_index)
                    else:
                        proportion_list.append((proportion, recoginze_index))
                        input_step3_mention_index.append(recoginze_index)
                '''
                temp_list = []
                if len(rec_pair) == 1:
                    proportion = 1
                else:
                    proportion = rec_pair[0]['score'] / (rec_pair[0]['score'] + rec_pair[1]['score'])
                for inner_pair in rec_pair:
                    temp_list.append(str(inner_pair['id']))
                input_step3_list.append(temp_list)
                if isMatch:
                    proportion_list.append((proportion, match_mention_index))
                    input_step3_mention_index.append(match_mention_index)
                else:
                    proportion_list.append((proportion, recoginze_index))
                    input_step3_mention_index.append(recoginze_index)
                recoginze_index -= 1
            proportion_list = sorted(proportion_list, key=lambda proportion: proportion[0])
            # print proportion_list
            five_input_index_set = set()
            add_number = 0
            for proportion in proportion_list:
                five_input_index_set.add(proportion[1])
                add_number += 1
                if add_number == 5:
                    break
            # print five_input_index_set
            new_input_step3_list = []
            new_input_step3_mention_index = []
            # print input_step3_list
            # print input_step3_mention_index
            for j in range(0, len(input_step3_list)):
                if input_step3_mention_index[j] in five_input_index_set:
                    new_input_step3_list.append(input_step3_list[j])
                    new_input_step3_mention_index.append(input_step3_mention_index[j])
                else:
                    new_input_step3_list.append([input_step3_list[j][0]])
                    new_input_step3_mention_index.append(input_step3_mention_index[j])
            # print new_input_step3_list
            # print new_input_step3_mention_index
            del input_step3_mention_index
            del input_step3_list
            if new_input_step3_list != []:
                print 'total sequence length is : %d' % (len(new_input_step3_list))
                # print input_step3_list
                graph_result = graph.get_final_entity_sequence_by_graph_embedding(new_input_step3_list)
                # print graph_result
                for j in range(0, len(graph_result)):
                    if graph_result[j] != '-1':
                        total_link += 1
                        if new_input_step3_mention_index[j] >= 0:
                            # print graph_result[j]
                            if id_entity_dict[graph_result[j]] == \
                                    post_list[i]['alias_entity'][new_input_step3_mention_index[j]]['entity']:
                                result_file.writelines('user mention: %d  ,  TP\n' % (new_input_step3_mention_index[j]))
                                TP += 1
                            else:
                                result_file.writelines('user mention: %d  ,  FN\n' % (new_input_step3_mention_index[j]))
                                FN += 1

                    '''
                    total_link += len(input_step3_list)
                    for j in range(0, len(input_step3_list)):
                        if input_step3_mention_index[j] >= 0:
                            if id_entity_dict[input_step3_list[j][0]] == \
                                    post_list[i]['alias_entity'][input_step3_mention_index[j]]['entity']:
                                result_file.writelines('user mention: %d  ,  TP\n' % (input_step3_mention_index[j]))
                                TP += 1
                            else:
                                result_file.writelines('user mention: %d  ,  FN\n' % (input_step3_mention_index[j]))
                                FN += 1
                                '''

    result_file.writelines('total alias-entity pair is %d\n' % (total))
    result_file.writelines('TP is %d\n' % (TP))
    result_file.writelines('FN is %d\n' % (FN))
    r = TP / float(TP + FN)
    result_file.writelines('mention recall is  %.7f\n' % ((TP + FN) / float(total)))
    result_file.writelines('link accuracy is  %.7f\n' % (r))
    result_file.writelines('total recognize mention  %d\n' % (total_recognize))
    result_file.writelines('total link mention  %d\n' % (total_link))
    result_file.writelines('mention precision is  %.7f\n' % ((TP + FN) / float(total_link)))
    # file.writelines('precision is %.7f\n' % (p))
    # file.writelines('recall is %.7f\n' % (r))
    # file.writelines('F1 is %.7f\n' % (2 * p * r / (p + r)))
    result_file.close()

def method2():
    graph = GraphUtil('data/graph embedding/graph_output.emb')
    # test paragraph
    # file = open('data/fel evaluation/step1-paragraph-test-new.txt', 'w')

    # test post
    result_file = open('data/fel evaluation/step3-post-test-v4.txt', 'w')

    id_entity_dict = {}
    with open('data/id-entity.tsv', 'r') as load_f:
        for line in load_f:
            content = line.split('\t')
            id_entity_dict[content[1].replace('\n', '')] = content[0]

    total = 0
    test_file = open('data/fel evaluation/batchset-9.json', 'r')
    post_list = json.load(test_file)
    for post in post_list:
        total += len(post['alias_entity'])

    TP = 0
    total_recognize = 0
    total_link = 0
    FN = 0
    with open('data/fel evaluation/predict-40-5-0.json', 'r') as load_f:
        load_dict = json.load(load_f)
        print 'total post number:  %d' % (len(load_dict))
        result_file.writelines('total lines is : %d\n' % (len(load_dict)))
        # print 'total lines is : %d' % (len(load_dict))
        # 每个帖子
        for i in range(0, len(load_dict)):
            pair_list = load_dict[i]['mention_entity']
            print i + 1
            result_file.writelines('current_line_index : %d,  post id : %s,  user labelled: %d\n' % (
                i + 1, post_list[i]['id'], len(post_list[i]['alias_entity'])))
            # print len(pair_list)
            total_recognize += len(pair_list)
            needMatch = []
            match_dict = {}
            match_index = 0
            for pair in post_list[i]['alias_entity']:
                needMatch.append((pair['begin_index'], pair['end_index']))
                match_dict[match_index] = False
                match_index += 1
            input_step3_list = []
            input_step3_mention_index = []
            # print needMatch
            # 每个识别出的mention集合
            recoginze_index = -1
            proportion_list = []
            for rec_pair in pair_list:
                temp_set = set()
                for inner_pair in rec_pair:
                    temp_set.add((inner_pair['begin'], inner_pair['end']))

                # print temp_set
                # 匹配当前list中是否有用户标记的mention
                match_mention_index = 0
                isMatch = False
                for need_match_pair in needMatch:
                    if match_dict[match_mention_index] == False:
                        if temp_set.isdisjoint(set([need_match_pair])) == False:
                            isMatch = True
                            match_dict[match_mention_index] == True
                            match_index -= 1
                            break
                    match_mention_index += 1

                '''
                if rec_pair[0]['id'] != -1:
                    temp_list = []
                    proportion = rec_pair[0]['score'] / (rec_pair[0]['score'] + rec_pair[1]['score'])
                    for inner_pair in rec_pair:
                        temp_list.append(str(inner_pair['id']))
                    input_step3_list.append(temp_list)
                    if isMatch:
                        proportion_list.append((proportion, match_mention_index))
                        input_step3_mention_index.append(match_mention_index)
                    else:
                        proportion_list.append((proportion, recoginze_index))
                        input_step3_mention_index.append(recoginze_index)
                '''
                temp_list = []
                if len(rec_pair) == 1:
                    proportion = 1
                else:
                    proportion = rec_pair[0]['score'] / (rec_pair[0]['score'] + rec_pair[1]['score'])
                for inner_pair in rec_pair:
                    temp_list.append(str(inner_pair['id']))
                input_step3_list.append(temp_list)
                if isMatch:
                    proportion_list.append((proportion, match_mention_index))
                    input_step3_mention_index.append(match_mention_index)
                else:
                    proportion_list.append((proportion, recoginze_index))
                    input_step3_mention_index.append(recoginze_index)
                recoginze_index -= 1
            iterator = len(input_step3_list) / 5
            new_input_step3_list = []
            new_input_step3_mention_index = []
            for j in range(0, iterator + 1):
                if j == iterator:
                    new_input_step3_list.extend(input_step3_list[j * 5:])
                    new_input_step3_mention_index.extend(input_step3_mention_index[j * 5:])
                else:
                    new_input_step3_list.extend(input_step3_list[j * 5:(j + 1) * 5])
                    new_input_step3_mention_index.extend(input_step3_mention_index[j * 5:(j + 1) * 5])
                graph_result = graph.get_final_entity_sequence_by_graph_embedding(new_input_step3_list)
                new_input_step3_list = []
                for result in graph_result:
                    new_input_step3_list.append([result])

            if new_input_step3_list != []:
                print 'total sequence length is : %d' % (len(new_input_step3_list))
                #print new_input_step3_list
                #print new_input_step3_mention_index
                for j in range(0, len(new_input_step3_list)):
                    if new_input_step3_list[j][0] != '-1':
                        total_link += 1
                        if new_input_step3_mention_index[j] >= 0:
                            #print new_input_step3_list[j]
                            if id_entity_dict[new_input_step3_list[j][0]] == post_list[i]['alias_entity'][new_input_step3_mention_index[j]]['entity']:
                                result_file.writelines('user mention: %d  ,  TP\n' % (new_input_step3_mention_index[j]))
                                TP += 1
                            else:
                                result_file.writelines('user mention: %d  ,  FN\n' % (new_input_step3_mention_index[j]))
                                FN += 1

    result_file.writelines('total alias-entity pair is %d\n' % (total))
    result_file.writelines('TP is %d\n' % (TP))
    result_file.writelines('FN is %d\n' % (FN))
    r = TP / float(TP + FN)
    result_file.writelines('mention recall is  %.7f\n' % ((TP + FN) / float(total)))
    result_file.writelines('link accuracy is  %.7f\n' % (r))
    result_file.writelines('total recognize mention  %d\n' % (total_recognize))
    result_file.writelines('total link mention  %d\n' % (total_link))
    result_file.writelines('mention precision is  %.7f\n' % ((TP + FN) / float(total_link)))
    # file.writelines('precision is %.7f\n' % (p))
    # file.writelines('recall is %.7f\n' % (r))
    # file.writelines('F1 is %.7f\n' % (2 * p * r / (p + r)))
    result_file.close()

def method3():
    graph = GraphUtil('data/graph embedding/graph_output.emb')
    # test paragraph
    # file = open('data/fel evaluation/step1-paragraph-test-new.txt', 'w')

    # test post
    result_file = open('data/fel evaluation/step3-post-test-v5.txt', 'w')

    id_entity_dict = {}
    with open('data/id-entity.tsv', 'r') as load_f:
        for line in load_f:
            content = line.split('\t')
            id_entity_dict[content[1].replace('\n', '')] = content[0]

    total = 0
    test_file = open('data/fel evaluation/batchset-9.json', 'r')
    post_list = json.load(test_file)
    for post in post_list:
        total += len(post['alias_entity'])

    TP = 0
    total_recognize = 0
    total_link = 0
    FN = 0
    with open('data/fel evaluation/predict-40-5-0.json', 'r') as load_f:
        load_dict = json.load(load_f)
        print 'total post number:  %d' % (len(load_dict))
        result_file.writelines('total lines is : %d\n' % (len(load_dict)))
        # print 'total lines is : %d' % (len(load_dict))
        # 每个帖子
        for i in range(0, len(load_dict)):
            pair_list = load_dict[i]['mention_entity']
            print i + 1
            result_file.writelines('current_line_index : %d,  post id : %s,  user labelled: %d\n' % (
                i + 1, post_list[i]['id'], len(post_list[i]['alias_entity'])))
            # print len(pair_list)
            total_recognize += len(pair_list)
            needMatch = []
            match_dict = {}
            match_index = 0
            for pair in post_list[i]['alias_entity']:
                needMatch.append((pair['begin_index'], pair['end_index']))
                match_dict[match_index] = False
                match_index += 1
            input_step3_list = []
            input_step3_mention_index = []
            # print needMatch
            # 每个识别出的mention集合
            recoginze_index = -1
            proportion_list = []
            for rec_pair in pair_list:
                temp_set = set()
                for inner_pair in rec_pair:
                    temp_set.add((inner_pair['begin'], inner_pair['end']))

                # print temp_set
                # 匹配当前list中是否有用户标记的mention
                match_mention_index = 0
                isMatch = False
                for need_match_pair in needMatch:
                    if match_dict[match_mention_index] == False:
                        if temp_set.isdisjoint(set([need_match_pair])) == False:
                            isMatch = True
                            match_dict[match_mention_index] == True
                            match_index -= 1
                            break
                    match_mention_index += 1

                '''
                if rec_pair[0]['id'] != -1:
                    temp_list = []
                    proportion = rec_pair[0]['score'] / (rec_pair[0]['score'] + rec_pair[1]['score'])
                    for inner_pair in rec_pair:
                        temp_list.append(str(inner_pair['id']))
                    input_step3_list.append(temp_list)
                    if isMatch:
                        proportion_list.append((proportion, match_mention_index))
                        input_step3_mention_index.append(match_mention_index)
                    else:
                        proportion_list.append((proportion, recoginze_index))
                        input_step3_mention_index.append(recoginze_index)
                '''
                temp_list = []
                if len(rec_pair) == 1:
                    proportion = 1
                else:
                    proportion = rec_pair[0]['score'] / (rec_pair[0]['score'] + rec_pair[1]['score'])
                for inner_pair in rec_pair:
                    temp_list.append(str(inner_pair['id']))
                input_step3_list.append(temp_list)
                if isMatch:
                    proportion_list.append((proportion, match_mention_index))
                    input_step3_mention_index.append(match_mention_index)
                else:
                    proportion_list.append((proportion, recoginze_index))
                    input_step3_mention_index.append(recoginze_index)
                recoginze_index -= 1
            iterator = len(input_step3_list) / 5
            #print iterator
            new_input_step3_list = []
            new_input_step3_mention_index = []
            for j in range(0, iterator + 1):
                #print j
                if j == iterator:
                    new_input_step3_list.extend(input_step3_list[j * 5:])
                    new_input_step3_mention_index.extend(input_step3_mention_index[j * 5:])
                else:
                    new_input_step3_list.extend(input_step3_list[j * 5:(j + 1) * 5])
                    new_input_step3_mention_index.extend(input_step3_mention_index[j * 5:(j + 1) * 5])
                #print new_input_step3_list
                if new_input_step3_list != []:
                    graph_result = graph.get_final_entity_sequence_by_graph_embedding(new_input_step3_list)
                    for j in range(0, len(graph_result)):
                        if graph_result[j] != '-1':
                            total_link += 1
                            if new_input_step3_mention_index[j] >= 0:
                                # print graph_result[j]
                                if id_entity_dict[graph_result[j]] == \
                                        post_list[i]['alias_entity'][new_input_step3_mention_index[j]]['entity']:
                                    result_file.writelines('user mention: %d  ,  TP\n' % (new_input_step3_mention_index[j]))
                                    TP += 1
                                else:
                                    result_file.writelines('user mention: %d  ,  FN\n' % (new_input_step3_mention_index[j]))
                                    FN += 1
                new_input_step3_list = []
                new_input_step3_mention_index = []

    result_file.writelines('total alias-entity pair is %d\n' % (total))
    result_file.writelines('TP is %d\n' % (TP))
    result_file.writelines('FN is %d\n' % (FN))
    r = TP / float(TP + FN)
    result_file.writelines('mention recall is  %.7f\n' % ((TP + FN) / float(total)))
    result_file.writelines('link accuracy is  %.7f\n' % (r))
    result_file.writelines('total recognize mention  %d\n' % (total_recognize))
    result_file.writelines('total link mention  %d\n' % (total_link))
    result_file.writelines('mention precision is  %.7f\n' % ((TP + FN) / float(total_link)))
    # file.writelines('precision is %.7f\n' % (p))
    # file.writelines('recall is %.7f\n' % (r))
    # file.writelines('F1 is %.7f\n' % (2 * p * r / (p + r)))
    result_file.close()

if __name__ == '__main__':
    method3()



