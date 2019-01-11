# encoding: utf-8
import jpype
from jpype import *
import nltk
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class FastLinker(object):
    def __init__(self, hash_file='data/fel evaluation/final.hash', jvm_path=jpype.getDefaultJVMPath(), jar_path='data/fel evaluation/FEL.jar'):
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
        words = []
        stop_word_list = set(nltk.corpus.stopwords.words('english'))
        for w in nltk.word_tokenize(query.lower()):
            if w not in stop_word_list:
                words.append(w)
        text = " ".join(words)
        javaLinkResult = self.javaLinker.linkText(text, limit)
        '''
        # print(javaLinkResult)
        result = []
        text = query.lower()
        for javaCandidates in javaLinkResult:
            mention = javaCandidates[0].s.span.split()
            start = text.index(mention[0])
            end = start + len(mention[0])
            text = text[end:]
            for m in mention[1:]:
                start = text.index(m)
                end = start + len(m)
            r = {'mention': javaCandidates[0].s.span, 'candidates': []}
            for entity in javaCandidates:
                r['candidates'].append({
                    'id': entity.id,
                    'name': entity.text.toString(),
                    'score': entity.score
                })
            result.append(r)
        return text, result
        '''
        return javaLinkResult

if __name__ == '__main__':
    file = open('data/fel evaluation/log-newest6.txt', 'w')
    matrix = [0] * 100
    id_entity_dict = {}
    with open('data/id-entity.tsv', 'r') as load_f:
        for line in load_f:
            content = line.split('\t')
            id_entity_dict[content[1].replace('\n', '')] = content[0]
    fel = FastLinker()
    '''
    javaLinkResult = fel.link('the API docs', 100)
    print len(javaLinkResult[0])
    for entityResult in javaLinkResult[0]:
        print entityResult.s.span
        print entityResult.id
    exit(1)
    '''
    total = 0
    current_line_index = 0
    current_pair_index = 0
    with open('data/train so post/post.json', 'r') as load_f:
        load_dict = json.load(load_f)
        file.writelines('total lines is : %d\n' % (len(load_dict)))
        #print 'total lines is : %d' % (len(load_dict))
        for post in load_dict:
            pair_list = post['alias_entity']
            current_line_index += 1
            total += len(pair_list)
            file.writelines('current_line_index : %d\n' % (current_line_index))
            #print 'current_line_index : %d' % (current_line_index)
            for pair in pair_list:
                current_pair_index += 1
                try:
                    print current_pair_index
                    file.writelines('current_pair_index : %d\n' % (current_pair_index))
                    file.writelines('origin alias is :  %s\n' % (pair['alias']))
                    file.writelines('origin entity is :  %s\n' % (pair['entity']))
                    #print 'current_pair_index : %d' % (current_pair_index)
                    #print 'origin alias is :  %s' % (pair['alias'])
                    #print 'origin entity is :  %s' % (pair['entity'])
                    javaLinkResult = fel.link(pair['alias'], 100)
                    index = 0
                    is_find = False
                    if len(javaLinkResult) > 0:
                        file.writelines('candidate number is :  %d\n' % (len(javaLinkResult[0])))
                        for entityResult in javaLinkResult[0]:
                            index += 1
                            entity_id = str(entityResult.id)
                            if len(entityResult.s.span) == 1:
                                index -= 1
                                continue
                            if entity_id != '-1':
                                if id_entity_dict[entity_id] == pair['entity']:
                                    file.writelines('find in %d result\n' % (index))
                                    #print 'find in %d result' % (index)
                                    is_find = True
                                    for i in range(index, 101):
                                        matrix[i - 1] += 1
                                    break
                        if is_find == False:
                            file.writelines('fel can not find correct candidate\n')
                    else:
                        file.writelines('do not have alias\n')
                            #print 'can not findjpype.startJVM(jvm_path, arg)
                except Exception, e:
                    file.writelines('illegal entity %s' % (pair['entity']))
    file.writelines('total alias-entity pair is %d\n' % (total))
    #print 'total alias-entity pair is %d' % (total)
    for i in range(0, 100):
        file.writelines('The percentage of positive sample in %d:  %.4f\n' % (i + 1, matrix[i] / float(total)))
        #print 'The percentage of positive sample in %d:  %.4f' % (i + 1, matrix[i] / float(total))
    file.close()
