# encoding: utf-8
import json

if __name__ == '__main__':
    # test paragraph
    #file = open('data/fel evaluation/step1-paragraph-test-new.txt', 'w')

    #test post
    result_file = open('data/fel evaluation/step2-post-test.txt', 'w')
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
        #print 'total lines is : %d' % (len(load_dict))
        #每个帖子
        for i in range(0, len(load_dict)):
            pair_list = load_dict[i]['mention_entity']
            print i + 1
            result_file.writelines('current_line_index : %d,  post id : %s,  user labelled: %d\n' % (i + 1, post_list[i]['id'], len(post_list[i]['alias_entity'])))
            #print len(pair_list)
            total_recognize += len(pair_list)
            needMatch = []
            match_dict = {}
            match_index = 0
            for pair in post_list[i]['alias_entity']:
                needMatch.append((pair['begin_index'], pair['end_index']))
                match_dict[match_index] = False
                match_index += 1
            #print needMatch
            # 每个识别出的mention集合
            for rec_pair in pair_list:
                temp_set = set()
                for inner_pair in rec_pair:
                    temp_set.add((inner_pair['begin'], inner_pair['end']))

                #print temp_set
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
                if isMatch:
                    if rec_pair[0]['id'] != -1:
                        total_link += 1
                        if rec_pair[0]['name'] == post_list[i]['alias_entity'][match_mention_index]['entity']:
                            TP += 1
                            result_file.writelines('user mention: %d  ,  TP\n' % (match_mention_index))
                        else:
                            FN += 1
                            result_file.writelines('user mention: %d  ,  FN\n' % (match_mention_index))
                if match_index == 0:
                    break

    result_file.writelines('total alias-entity pair is %d\n' % (total))
    result_file.writelines('TP is %d\n' % (TP))
    result_file.writelines('FN is %d\n' % (FN))
    r = TP / float(TP + FN)
    result_file.writelines('mention recall is  %.7f\n' % ((TP + FN) / float(total)))
    result_file.writelines('link accuracy is  %.7f\n' % (r))
    result_file.writelines('total recognize mention  %d\n' % (total_recognize))
    result_file.writelines('total link mention  %d\n' % (total_link))
    result_file.writelines('mention precision is  %.7f\n' % ((TP + FN) / float(total_link)))
    #file.writelines('precision is %.7f\n' % (p))
    #file.writelines('recall is %.7f\n' % (r))
    #file.writelines('F1 is %.7f\n' % (2 * p * r / (p + r)))
    result_file.close()