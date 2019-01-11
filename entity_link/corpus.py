# encoding: utf-8
import codecs
import json
#import MySQLdb
import nltk


"""

it' goal is to find the count from corpus.
FEAT = LOAD '$feat' USING PigStorage('\t') AS (
    alias:chararray,
    phrase_freq:long,
    alias_freq:long,
    entity_id:chararray,
    alias_entity_freq:long
);
{
    "alias":"",
    "link":"",
    "count":"",
}

"""


class EntityCFNameToEntityIDDataGenerate:
    def __init__(self):
        pass


"""
process the alias to lower case.
"""


class ProcessorAliasCount:
    #def __init__(self):
        #self.tokenizer = StanfordTokenizer()

    def process_alias_2_entity_map(self, old_vocabulary_path, new_vocabulary_path):
        """
        process the alias in
        :return:
        """
        print 'process alias to normalize'
        with codecs.open(old_vocabulary_path, 'r', 'utf-8') as f:
            vocabulary_list = json.load(f)

        new_vocabulary_list=[]
        index = 1
        for item in vocabulary_list:
            if index % 10000 == 0:
                print index
            alias = item["alias"]
            if not alias:
                continue
            alias = alias.strip()
            new_tokenize_alias = nltk.word_tokenize(alias)
            #new_tokenize_alias = self.tokenizer.tokenize(alias)

            new_alias = " ".join(new_tokenize_alias).lower()
            #print("alias=", alias, " new_alias=", new_alias)

            item["alias"] = new_alias
            item["entity"] = item["link"]
            del item["link"]
            new_vocabulary_list.append(item)
            index += 1
        with codecs.open(new_vocabulary_path, 'w', 'utf-8') as f:
            json.dump(new_vocabulary_list, f)


class AliasStatisticsUtil:
    def __init__(self, alias_ngram=False):
        self.label_vocabulary = set([])
        self.max_label_length = 15
        self.alias_to_phrase_freq_count = {}
        self.vocabulary_path = None
        self.alias_ngram = alias_ngram

    def init_vocabulary_from_json(self, vocabulary_path):

        vocabulary_list = []
        alias_to_phrase_freq_count = {}
        with codecs.open(vocabulary_path, 'r', 'utf-8') as f:
            self.vocabulary_path = vocabulary_path
            vocabulary_list = json.load(f)
        label_vocabulary = set([])
        for item in vocabulary_list:
            alias = item["alias"]
            label_vocabulary.add(alias)
            # phrase_freq = 0
            # entity_id = item["entity"]
            # alias_freq = item["count"]
            # alias_entity_freq = item["count"]
        self.label_vocabulary = label_vocabulary
        print"labelVocabulary size=%d" % (len(label_vocabulary))
        print "max_label_length=%d"% (self.max_label_length)
        for alias in self.label_vocabulary:
            alias_to_phrase_freq_count[alias] = 0
        self.alias_to_phrase_freq_count = alias_to_phrase_freq_count

    def count_occur_from_json(self, corpus_json_path):
        print 'begin count occur from %s' % (corpus_json_path)
        index = 0
        with codecs.open(corpus_json_path, 'r', 'utf-8') as f:
            corpus_list = json.load(f)
            for corpus in corpus_list:
                self.count_occur_in_content(corpus["clean_text"])
                index += 1
                if index % 10000 == 0:
                    print 'finish %d' % (index)
        print 'finish count occur from %s' % (corpus_json_path)

    def count_occur_from_file(self, file_path):
        print 'begin count occur from %s' % (file_path)
        index = 0
        '''
        with codecs.open(file_path, 'r', 'utf-8') as f:
            for line in f:
                #self.count_occur_in_content(line)
                index += 1
                print index
                if index % 10000 == 0:
                    print 'finish %d' % (index)
        print 'finish count occur from %s' % (file_path)
        '''
        with open(file_path, 'r') as f:
            line = f.readline().decode('utf-8', 'ignore')
            while line:
                try:
                    self.count_occur_in_content(line)
                except Exception:
                    print line
                index += 1
                if index % 10000 == 0:
                    print 'finish %d' % (index)
                line = f.readline().decode('utf-8', 'ignore')
        print index
        print 'finish count occur from %s' % (file_path)

    def count_occur_in_content(self, content):
        label_vocabulary = self.label_vocabulary
        alias_to_phrase_freq_count = self.alias_to_phrase_freq_count
        max_label_length = self.max_label_length
        if content == None or content == "":
            return
        words = nltk.word_tokenize(content)
        content = " ".join(words).lower()
        match_index_list = []
        for i, char in enumerate(content):
            if self.is_white_char(content[i]):
                match_index_list.append(i)

        len_match_index_list = len(match_index_list)
        for i in range(0, len_match_index_list - 1):
            start_index = match_index_list[i] + 1
            if self.is_white_char(content[start_index]):
                continue
            max_word_index = min(i + max_label_length, len_match_index_list - 1)
            for j in range(max_word_index, i, -1):
                current_index = match_index_list[j]
                ngram = content[start_index:current_index]
                if ngram in label_vocabulary:
                    alias_to_phrase_freq_count[ngram] = alias_to_phrase_freq_count[ngram] + 1

        self.alias_to_phrase_freq_count = alias_to_phrase_freq_count

    def is_white_char(self, char):
        if char == " " or char == "\n" or char == "\t":
            return True
        return False

    def add_mysql_alias_to_system(self):
        new_alias_from_mysql_alias = {}
        with open('data/mysql_alias.tsv', 'r') as f:
            index = 0
            for line in f:
                content = line.split('\t')
                new_alias = content[0] + '###' + content[1][:-1]
                new_alias_from_mysql_alias[new_alias] = 1
                self.alias_to_phrase_freq_count[content[0]] = self.alias_to_phrase_freq_count.get(content[0], 0) + 1
                index += 1
            print 'finish mysql alias pair : %d' % (index)
        with codecs.open(self.vocabulary_path, 'r', 'utf-8') as f:
            vocabulary_list = json.load(f)
            print 'origin alias-entity pair number : %d' % (len(vocabulary_list))
            for item in vocabulary_list:
                new_alias = item['alias'] + '###' + item["entity"]
                new_alias_from_mysql_alias[new_alias] = new_alias_from_mysql_alias.get(new_alias, 0) + item['count']
        list_content = []
        for key in new_alias_from_mysql_alias:
            alias_entity = key.split('###')
            alias = alias_entity[0]
            entity_id = alias_entity[1]
            new_dict = {}
            new_dict['count'] = new_alias_from_mysql_alias[key]
            new_dict['alias'] = alias
            new_dict['entity'] = entity_id
            list_content.append(new_dict)
        print 'after join new alias, alias-entity pair number : %d   ,  %d' % (len(new_alias_from_mysql_alias), len(list_content))
        del new_alias_from_mysql_alias
        with codecs.open(self.vocabulary_path, 'w', 'utf-8') as f:
            json.dump(list_content, f)

    def output_intermediate_data(self):
        with codecs.open('data/phrase_dict', 'w', 'utf-8') as f:
            for key in self.alias_to_phrase_freq_count:
                f.write('%s\t%d\n' % (key, self.alias_to_phrase_freq_count[key]))

    def partial_run(self, vocabulary_path):
        print 'partial run begin'
        self.vocabulary_path = vocabulary_path
        with open('data/without so/phrase_dict', 'r') as f:
            line = f.readline().decode('utf-8', 'ignore')
            while line:
                content = line.split('\t')
                self.alias_to_phrase_freq_count[content[0]] = content[1][:-1]
                line = f.readline().decode('utf-8', 'ignore')
        print 'partial run finish'
        print 'alias number: %d' % (len(self.alias_to_phrase_freq_count))

    def write_to_tsv(self, tsv_path):
        print 'begin write to %s' %(tsv_path)
        with codecs.open(self.vocabulary_path, 'r', 'utf-8') as f:
            vocabulary_list = json.load(f)
            #print(self.alias_to_phrase_freq_count)
            print 'read file from %s, total alias-entity pair is : %d' % (self.vocabulary_path, len(vocabulary_list))
            index = 0
            result_list = []
            with codecs.open(tsv_path, 'w', 'utf-8') as tsv_f:
                for item in vocabulary_list:
                    alias = item["alias"]
                    phrase_freq = self.alias_to_phrase_freq_count.get(alias, 0)
                    entity_id = item["entity"]
                    alias_freq = item["count"]
                    alias_entity_freq = item["count"]
                    left_part = "\t".join([alias, str(phrase_freq), str(alias_freq),entity_id, str(alias_entity_freq)])
                    result_list.append(left_part)
                    index += 1
                    if index % 10000 == 0:
                        print 'finish %d to tsv' % (index)
                tsv_f.write('\n'.join(result_list))
