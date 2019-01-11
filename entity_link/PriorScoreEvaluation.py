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

    def quick_link(self, query):
        javaLinkResult = self.javaLinker.quicklinkText(query)
        return javaLinkResult

if __name__ == '__main__':
    file = open('data/fel evaluation/prior_probability_.txt', 'w')
    total_matrix = [0] * 201
    null_matrix = [0] * 201
    id_entity_dict = {}
    with open('data/id-entity.tsv', 'r') as load_f:
        for line in load_f:
            content = line.split('\t')
            id_entity_dict[content[1].replace('\n', '')] = content[0]
    fel = FastLinker()
    current_alias_index = 0
    total_pair = 0
    wrong = 0
    use_dict = {}
    with open('data/normalize_alias_link.json', 'r') as load_f:
        load_dict = json.load(load_f)
        file.writelines('total lines is : %d\n' % (len(load_dict)))
        #print 'total lines is : %d' % (len(load_dict))
        for post in load_dict:
            if post['alias'] not in use_dict:
                use_dict[post['alias']] = 1
                javaLinkResult = fel.quick_link(post['alias'])
                current_alias_index += 1
                print current_alias_index
                for entityResult in javaLinkResult:
                    total_pair += 1
                    score = entityResult.score
                    if score > 0:
                        wrong += 1
                        score = -0.01
                    score_str = str(score)
                    left = int(score_str[score_str.index('-') + 1: score_str.index('.')])
                    right = int(score_str[score_str.index('.') + 1][0])
                    if left < 20:
                        total_matrix[left * 10 + right] += 1
                        if entityResult.id == -1:
                            null_matrix[left * 10 + right] += 1
                    else:
                        total_matrix[200] += 1
                        if entityResult.id == -1:
                            null_matrix[200] += 1
    print 'wrong number is %d' % (wrong)
    file.writelines('total pair is : %d\n' % (total_pair))
    for i in range(0, 201):
        file.writelines('The number of probability sample in %d ,  total: %d,  NULL:  %d\n' % (i, total_matrix[i], null_matrix[i]))
        #print 'The percentage of positive sample in %d:  %.4f' % (i + 1, matrix[i] / float(total))
    file.close()