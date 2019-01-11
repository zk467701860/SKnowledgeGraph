# encoding: utf-8
import jpype
from jpype import *
import nltk
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class FastLinker(object):
    def __init__(self, hash_file='data/fel evaluation/final.hash', jvm_path=jpype.getDefaultJVMPath(), jar_path='data/fel evaluation/FEL-001.jar'):
        arg = '-Djava.class.path=%s' % jar_path
        if not jpype.isJVMStarted():
            try:
                jpype.startJVM(jvm_path, arg)
            except RuntimeError:
                print("illegal JVM path!")
                exit(1)
        JavaLinker = JClass("com.yahoo.semsearch.fastlinking.FastEntityLinker")
        self.javaLinker = JavaLinker(hash_file)

    def link(self, query, limit=10):
        text = query.lower()
        words = []
        stop_word_list = nltk.corpus.stopwords.words('english')
        for w in nltk.word_tokenize(text):
            if w not in stop_word_list:
                words.append(w)
        new_text = " ".join(words)
        javaLinkResult = self.javaLinker.linkText(new_text, limit)
        result = []
        beg = 0
        #print 'get mention : %d' % (len(javaLinkResult))
        for javaCandidates in javaLinkResult:
            # print([e.s.span for e in javaCandidates])
            mention_index = {}

            mentions = sorted(set([c.s.span for c in javaCandidates]), key=lambda m: len(m))
            longest = mentions[-1]
            words = longest.split()
            cur_mention = words[0]
            begin = text.find(words[0], beg)

            if begin < 0:
                continue
            end = begin + len(words[0])
            beg = end
            mention_index[words[0]] = {
                "begin": begin,
                "end": end
            }

            for w in words[1:]:
                temp_text = text[end:]
                last = len(temp_text)
                temp_text = temp_text.lstrip()
                now = len(temp_text)

                if temp_text[:len(w)] == w:
                    end += last - now + len(w)
                    cur_mention += (" %s" % w)
                    mention_index[cur_mention] = {
                        "begin": begin,
                        "end": end
                    }
                else:
                    break
            # print(mention_index)
            candidates = []
            id_set = set()
            for c in javaCandidates:
                if c.id in id_set:
                    continue
                m = c.s.span
                if len(m) == 1:
                    continue
                if m not in mention_index:
                    # print(m)
                    continue
                begin = mention_index[m]["begin"]
                end = mention_index[m]["end"]
                candidates.append({
                    "mention": text[begin:end],
                    "id": c.id,
                    "name": c.text,
                    "begin": begin,
                    "end": end,
                    "score": c.score
                })
                id_set.add(c.id)
            if len(candidates) != 0:
                result.append(candidates)

        return result

if __name__ == '__main__':

    # test paragraph
    #file = open('data/fel evaluation/step1-paragraph-test-new.txt', 'w')

    #test post
    result_file = open('data/fel evaluation/step1-post-test.txt', 'w')

    fel = FastLinker()
    total = 0
    current_line_index = 0
    TP = 0
    total_recognize = 0
    total_link = 0
    FN = 0
    with open('data/fel evaluation/batchset-9.json', 'r') as load_f:
        load_dict = json.load(load_f)
        print 'total post number:  %d' % (len(load_dict))
        #file.writelines('total lines is : %d\n' % (len(load_dict)))
        #print 'total lines is : %d' % (len(load_dict))
        for post in load_dict:
            pair_list = post['alias_entity']
            current_line_index += 1
            print 'line index: %d, user mention total: %d' % (current_line_index, len(pair_list))
            total += len(pair_list)
            needMatch = []
            match_dict = {}
            match_index = 0
            for pair in pair_list:
                needMatch.append((pair['begin_index'], pair['end_index']))
                match_dict[match_index] = False
                match_index += 1
            # test paragraph
            #file.writelines('current_line_index : %d, paragraph_id: %d,  post id : %s\n' % (current_line_index, post['paragraph_id'], post['post_id']))

            #test post
            result_file.writelines('current_line_index : %d,  post id : %s\n' % (current_line_index, post['id']))

            #print 'current_line_index : %d' % (current_line_index)
            javaLinkResult = fel.link(post['text'], 40)
            total_recognize += len(javaLinkResult)
            for entityResult in javaLinkResult:
                if entityResult[0]['id'] != -1:
                    total_link += 1
            result_file.writelines('FEL recognize mention: %d  ,  user mention: %d\n' % (len(javaLinkResult), len(needMatch)))
            #print needMatch
            current_list_index = 0
            for entityResult in javaLinkResult:
                temp_set = set()
                for inner_pair in entityResult:
                    temp_set.add((inner_pair['begin'], inner_pair['end']))

                #print temp_set
                #匹配当前list中是否有用户标记的mention
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
                    if entityResult[0]['id'] != -1:
                        if entityResult[0]['name'] == pair_list[match_mention_index]['entity']:
                            TP += 1
                            result_file.writelines('mention index: %s ,  TP\n' % (match_mention_index))
                        else:
                            FN += 1
                            result_file.writelines('user mention: %d  ,  FN\n' % (match_mention_index))
                if match_index == 0:
                    print 'find all user mention in %d' % (current_list_index)
                    break
                current_list_index += 1

    result_file.writelines('total alias-entity pair is %d\n' % (total))
    result_file.writelines('TP is %d\n' % (TP))
    result_file.writelines('FN is %d\n' % (FN))
    r = TP / float(TP + FN)
    result_file.writelines('mention recall is  %.7f\n' % ((TP + FN) / float(total)))
    result_file.writelines('link accuracy is  %.7f\n' % (r))
    result_file.writelines('total recognize mention  %d\n' % (total_recognize))
    result_file.writelines('total link mention  %d\n' % (total_link))
    result_file.writelines('mention precision is  %.7f\n' % ((TP + FN) / float(total_link)))
    #file.writelines('recall is %.7f\n' % (r))
    #file.writelines('F1 is %.7f\n' % (2 * p * r / (p + r)))
    result_file.close()
