# -*- coding:utf8 -*-
import sys
import unicodedata
import re
import string
import nltk.corpus
import os

reload(sys)
sys.setdefaultencoding('utf8')

class CountSystem():
    #带有包含pig2内容的各条目合并计算的部分
    def count(self):
        alias_anchor_dict = {}
        alias_phrase_dict = {}
        alias_entity_pair_dict = {}
        entity_dict = {}
        with open('alias-entity-counts.tsv') as f:
            for line in f:
                values = line.split('\t')
                origin_alias = values[0]
                # alias = origin_alias
                print origin_alias
                alias = self.normalize(origin_alias)
                #print alias
                phrase_freq = int(values[1])
                #print phrase_freq
                entity_id = values[3]
                #print entity_id
                alias_entity_freq = int(values[4])
                #print alias_entity_freq
                if alias not in alias_anchor_dict:
                    alias_anchor_dict[alias] = alias_entity_freq
                else:
                    alias_anchor_dict[alias] += alias_entity_freq
                if alias not in alias_phrase_dict:
                    temp_set = set()
                    temp_set.add(phrase_freq)
                    alias_phrase_dict[alias] = temp_set
                else:
                    temp_set = alias_phrase_dict[alias]
                    #print '%s  %s' % (alias, type(alias))
                    #print '%s  %s' % (temp_set, type(temp_set))
                    #print phrase_freq
                    #print type(phrase_freq)
                    temp_set.add(phrase_freq)
                    alias_phrase_dict[alias] = temp_set
                    #print alias_phrase_dict[alias]
                pair = alias + '###' + entity_id
                if pair not in alias_entity_pair_dict:
                    alias_entity_pair_dict[pair] = alias_entity_freq
                else:
                    alias_entity_pair_dict[pair] += alias_entity_freq
                if entity_id not in entity_dict:
                    entity_dict[entity_id] = alias_entity_freq
                else:
                    entity_dict[entity_id] += alias_entity_freq
        for alias_phrase in alias_phrase_dict:
            phrase_set = alias_phrase_dict[alias_phrase]
            count = 0
            #print phrase_set
            for ele in phrase_set:
                #print 'ele %d' % (ele)
                count += ele
            alias_phrase_dict[alias_phrase] = count
        with open('output_phase.tsv', 'w') as f:
            for alias_entity_pair in alias_entity_pair_dict:
                alias_entity = alias_entity_pair.split('###')
                alias = alias_entity[0]
                entity_id = alias_entity[1]
                alias_count = alias_anchor_dict[alias]
                alias_phrase_count = alias_phrase_dict[alias]
                entity_count = entity_dict[entity_id]
                alias_entity_count = alias_entity_pair_dict[alias_entity_pair]
                f.writelines("%s\t%d\t%d\t%s\t%d\t%d\n" % (alias, alias_count, alias_phrase_count, entity_id, entity_count, alias_entity_count))
                f.flush()

    # 仅仅增加了entity_freq的合并内容的不包含pig2的内容,还去除了别名中的stop words
    def new_count(self, input_file_path):
        alias_anchor_dict = {}
        alias_phrase_dict = {}
        alias_entity_pair_dict = {}
        entity_dict = {}
        #with open('D:/Test/run/our/complete/pig1 before/alias-entity-counts.tsv') as f:
        entity_id_list = []
        with open(input_file_path) as f:
            for line in f:
                values = line.split('\t')
                #print values[0]
                entity_id = values[3]
                entity_id_list.append(entity_id)
                alias_entity_freq = int(values[4])
                if entity_id not in entity_dict:
                    entity_dict[entity_id] = alias_entity_freq
                else:
                    entity_dict[entity_id] += alias_entity_freq
        print 'entity number:  %d' % (len(entity_dict))
        stop_word_list = nltk.corpus.stopwords.words('english')
        output_file_path = 'temp.tsv'
        with open(input_file_path, 'r') as f:
            #output_file = open('D:/Test/run/our/complete/pig1 after/alias-entity-counts.tsv', 'w')
            output_file = open(output_file_path, 'w')
            index = 0
            for line in f:
                values = line.split('\t')
                origin_alias = values[0]
                # alias = origin_alias
                print '%d,  %s' % (index, origin_alias)
                alias = self.normalize(origin_alias, True)
                if alias != '' and alias not in stop_word_list:
                    #print alias
                    phrase_freq = int(values[1])
                    #print phrase_freq
                    alias_freq = int(values[2])
                    # print alias_freq
                    entity_id = entity_id_list[index]
                    #print entity_id
                    alias_entity_freq = int(values[4])
                    #print alias_entity_freq
                    output_file.writelines("%s\t%d\t%d\t%s\t%d\t%d\n" % (alias, alias_freq, phrase_freq, entity_id, entity_dict[entity_id], alias_entity_freq))
                    output_file.flush()
                    print 'meaningful alias'
                index += 1
            output_file.close()
        with open(output_file_path, 'r') as fread:
            with open(input_file_path, 'w') as fwrite:
                for line in fread:
                    fwrite.writelines(line)
        os.remove(output_file_path)

    #reserveJavaPunct表示是否包含软件领域中有关的标点：'.' '*' '(' ')' ','
    def normalize(self, text, reserveJavaPunct):
        utf8_text = unicode(text, "utf-8")
        #unicode_norm = unicodedata.normalize('NFD', utf8_text)
        #print 'utf8_norm:  %s' % (unicode_norm)
        #unicode_pattern = re.compile(r'\\p{CombiningDiacriticalMarks}+')
        #unicode_0 = unicode_pattern.sub('', unicode_norm)
        #print 'unicode_0:  %s' % (unicode_0)
        ascii_norm = unicodedata.normalize('NFD', utf8_text).encode('ascii', 'ignore')
        if reserveJavaPunct == False:
            punct_pattern = re.compile('[%s]' % re.escape(string.punctuation))
        else:
            punct_pattern = re.compile(r'[\\’!"#$%&\'\+\-/:;=@^`{|}~]+')
        #punct_pattern = re.compile(r"\p{Punct}+")
        ascii_1 = punct_pattern.sub(' ', ascii_norm)
        #print 'ascii_1:  %s' % (ascii_1)
        control_pattern = re.compile('[\x00-\x1F\x7F]')
        ascii_2 = control_pattern.sub(' ', ascii_1)
        #print 'ascii_2:  %s' % (ascii_2)
        space_pattern = re.compile('\s+')
        ascii_3 = space_pattern.sub(' ', ascii_2)
        #print 'ascii_3:  %s' % (ascii_3)
        if re.compile('[%s]' % re.escape(string.punctuation)).sub('', ascii_3).strip() == '':
            return ''
        return ascii_3.strip()

if __name__ == '__main__':
    #print nltk.corpus.stopwords.words('english')
    #print nltk.word_tokenize('add(1, 2)')
    #print transform_url_to_qualifier('http://docs.oracle.com/javase/7/docs/api/java/util/Objects.html#equals(java.lang.Object,%20java.lang.Object)')
    system = CountSystem()
    #system.new_count('data/alias-entity-counts_3.tsv')
    #print system.transform_url_to_qualifier('https://developers.google.cn/android/reference/com/google/android/gms/common/api/GoogleApiClient.html#hasConnectedApi(com.google.android.gms.common.api.Api%3C?%3E)')

    #new_str = 'Žvaigždės ' + chr(8) + 'aukštybėj .užges'
    #print new_str
    #print system.normalize(new_str)
    print system.normalize('documentation for java.lang.Double.NaN', True)
    #print system.normalize('files.newbytechannel ( java.nio.file.path , java.util.set < ? extends', True)

    #system.new_count()
    #print system.normalize('java.util.arraylist', True)
    #a_dict = {}
    #a_set = set()
    #a_set.add(1)
    #a_dict['abc'] = a_set
    #print a_dict['abc']
    #temp_set = a_dict['abc']
    #print temp_set
    #phrase_freq = 1
    #temp_set.add(phrase_freq)
    #print temp_set
    #a_dict['abc'] = temp_set
    #print a_dict['abc']
    '''
    entity_id = 'https://docs.oracle.com/javase/8/docs/api/javax/swing/text/html/../../../../javax/swing/text/AbstractWriter.html'
    prefix = entity_id[0:entity_id.index('//') + 2]
    post_fix = entity_id[entity_id.index('//') + 2:]
    entity_list = post_fix.split('/')
    begin_index = 0
    count = 0
    for i in range(0, len(entity_list)):
        if entity_list[i] == '..':
            if begin_index == 0:
                begin_index = i
            count += 1
        elif begin_index != 0:
            break
    if begin_index != 0:
        new_entity_id = prefix
        for i in range(0, begin_index - count):
            new_entity_id += entity_list[i] + '/'
        for i in range(begin_index + count, len(entity_list)):
            new_entity_id += entity_list[i] + '/'
        new_entity_id = new_entity_id[:-1]
        entity_id = new_entity_id
    print entity_id
    '''
    #stop_word_list = list(set(nltk.corpus.stopwords.words('english')))
    #print stop_word_list