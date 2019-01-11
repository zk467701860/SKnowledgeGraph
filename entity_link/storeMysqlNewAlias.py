# encoding: utf-8
import MySQLdb
import nltk
import codecs
import json

def store_mysql_alias_file():
    print 'begin add mysql alias'
    try:
        conn = MySQLdb.connect(host='10.141.221.73', user='root', passwd='root', port=3306, db='codehub',
                               charset='utf8')
        cur = conn.cursor()
    except MySQLdb.Error, e:
        print "Mysql connection Error %d: %s" % (e.args[0], e.args[1])
    aliasid_alias_dict = {}
    try:
        sql = 'select * from java_api_alias'
        cur.execute(sql)
        data = cur.fetchall()
        if data != ():
            print 'alias number : %d' % (len(data))
            for pair in data:
                aliasid_alias_dict[pair[0]] = pair[1]
        print 'finish construct aliasid_alias_dict'
    except Exception as e:
        print('MySQL: %s   error:%s' % (sql, e))
    id_entity_dict = {}  # int -> str
    with open('data/train so post/id-entity.tsv', 'r') as load_f:
        for line in load_f:
            content = line.split('\t')
            id_entity_dict[int(content[1][:-1])] = content[0]
    print 'finish construct id_entity_dict'
    new_alias_from_mysql_alias = {}
    try:
        sql = 'select * from has_alias'
        cur.execute(sql)
        data = cur.fetchall()
        if data != ():
            print 'join %d alias-entity pair' % (len(data))
            index = 0
            for pair in data:
                try:
                    if pair[0] in id_entity_dict:
                        alias = aliasid_alias_dict[pair[1]]
                        alias = alias.strip()
                        new_tokenize_alias = nltk.word_tokenize(alias)
                        new_alias = " ".join(new_tokenize_alias).lower()
                        entity = id_entity_dict[pair[0]]
                        new_alias_from_mysql_alias[new_alias + '###' + entity] = 1
                    index += 1
                    if index % 50000 == 0:
                        print 'finish mysql alias:  %d' % (index)
                        print 'inner alias-pair number is :  %d' % (len(new_alias_from_mysql_alias))
                except Exception as e:
                    print 'index:  %d,  error:  %s' % (index, pair[0])
    except Exception as e:
        print'MySQL: %s   error:%s' % (sql, e)
    print 'finish add alias to phrase freq dict'
    print 'current alias-pair number is :  %d' % (len(new_alias_from_mysql_alias))
    del aliasid_alias_dict
    try:
        print 'begin add extra method alias and parameter to type alias'
        sql = 'select id,qualified_name,full_declaration from java_all_api_entity where api_type = 11'
        cur.execute(sql)
        data = cur.fetchall()
        if data != ():
            print 'method count : %d' % (len(data))
            finish_method_count = 0
            new_alias_count = 0
            for pair in data:
                if pair[0] in id_entity_dict:
                    entity = id_entity_dict[pair[0]]
                    left_pos = pair[2].index('(')
                    right_pos = pair[2].index(')')
                    is_legal = True
                    if '<' in pair[2]:
                        begin_cal = False
                        for letter in pair[2]:
                            if letter == '<':
                                begin_cal = True
                            elif letter == ',':
                                if begin_cal:
                                    is_legal = False
                                    break;
                            elif letter == '>':
                                begin_cal = False
                    if left_pos != right_pos - 1 and is_legal:
                        method_name = pair[2][:left_pos].split()[-1]
                        parameter_list = pair[2][left_pos + 1:right_pos].split(',')
                        type_list = []
                        para_list = []
                        for parameter_pair in parameter_list:
                            content = parameter_pair.strip().split()
                            type_list.append(content[0])
                            para_list.append(content[1])
                        alias_list = []
                        alias_list.append(method_name)
                        # alias 1 (简单方法名+简单类型名)
                        alias = method_name + '('
                        # alias_list.append(alias)
                        for i in range(0, len(type_list)):
                            alias += type_list[i]
                            # alias_list.append(alias)
                            alias += ','
                        alias = alias[:-1] + ')'
                        alias_list.append(alias)

                        # alias 2 (简单方法名+简单类型名+形参名)
                        alias = method_name + '('
                        #alias_list.append(alias)
                        for i in range(0, len(type_list)):
                            alias += type_list[i]
                            #alias_list.append(alias)
                            alias += ' ' + para_list[i]
                            #alias_list.append(alias)
                            alias += ','
                        alias = alias[:-1] + ')'
                        alias_list.append(alias)

                        # alias 3 (简单方法名+形参名)
                        alias = method_name + '('
                        for i in range(0, len(type_list)):
                            alias += para_list[i]
                            #alias_list.append(alias)
                            alias += ','
                        alias = alias[:-1] + ')'
                        alias_list.append(alias)

                        for alias in alias_list:
                            new_alias_count += 1
                            new_tokenize_alias = nltk.word_tokenize(alias)
                            new_alias = " ".join(new_tokenize_alias).lower()
                            new_alias_from_mysql_alias[new_alias + '###' + entity] = 1

                        qualified_type_list = pair[1][pair[1].index('(') + 1:pair[1].index(')')].split(',')
                        # parameter alias(形参名与相对应类型名)
                        for i in range(0, len(type_list)):
                            head_char_string = type_list[i][0].lower()
                            for letter in type_list[i][1:]:
                                if ord(letter) >= 65 and ord(letter) <= 90:
                                    head_char_string += chr(ord(letter) + 32)
                            if len(para_list[i]) > 1 and (para_list[i].lower() in type_list[i].lower() or para_list[
                                i].lower() == head_char_string):
                                new_tokenize_alias = nltk.word_tokenize(para_list[i].lower())
                                new_alias = " ".join(new_tokenize_alias).lower()
                                new_alias_from_mysql_alias[new_alias + '###' + qualified_type_list[i]] = 1
                                new_alias_count += 1
                finish_method_count += 1
                if finish_method_count % 5000 == 0:
                    print 'finish method alias:  %d' % (finish_method_count)
                    print 'next inner alias-pair number is :  %d' % (len(new_alias_from_mysql_alias))
        print 'finish add extra method alias and parameter to type alias, add %d' % (new_alias_count)
    except Exception as e:
        print('MySQL: %s   error:%s' % (sql, e))
    print 'final alias-pair number is :  %d' % (len(new_alias_from_mysql_alias))
    del id_entity_dict
    with open('data/mysql_alias.tsv', 'w') as f:
        for key in new_alias_from_mysql_alias:
            alias_entity = key.split('###')
            alias = alias_entity[0]
            entity_id = alias_entity[1]
            f.writelines("%s\t%s\n" % (alias, entity_id))

def testFile():
    with open('data/mysql_alias.tsv', 'r') as f:
        index = 0
        for line in f:
            content = line.split('\t')
            new_alias = content[0] + '###' + content[1][:-1]
            index += 1
        print 'finish mysql alias pair : %d' % (index)

def testStopWords():
    stop_word_list = nltk.corpus.stopwords.words('english')
    wrong_word_dict = {}
    for word in stop_word_list:
        wrong_word_dict[word] = 1
    del stop_word_list
    special_word_list = ['call', 'return', 'error', 'exception', 'class', 'method', 'field', 'package', 'interface']
    for word in special_word_list:
        wrong_word_dict[word] = 1
    del special_word_list
    print wrong_word_dict

def testWriteMultiRows():
    with codecs.open('data/test1.txt', 'w', 'utf-8') as f:
        test_buffer = ''
        alias = 'abc'
        left_part = 'aaa'
        test_buffer += '\t'.join([alias, left_part]) + '\n'
        test_buffer += '\t'.join([alias, left_part]) + '\n'
        test_buffer += '\t'.join([alias, left_part]) + '\n'
        test_buffer += '\t'.join([alias, left_part]) + '\n'
        f.writelines(test_buffer)

def testReadAndWriteFile():
    list_content = []
    with codecs.open('data/normalize_alias_link.json', 'r', 'utf-8') as f:
        vocabulary_list = json.load(f)
        print 'origin alias-entity pair number : %d' % (len(vocabulary_list))
        for item in vocabulary_list:
            new_dict = {}
            new_dict['alias'] = item['alias']
            list_content.append(new_dict)
    with codecs.open('data/normalize_alias_link.json', 'w', 'utf-8') as f:
        json.dump(list_content, f)

if __name__ == '__main__':
    #store_mysql_alias_file()
    #testFile()
    #testStopWords()
    #testWriteMultiRows()
    testReadAndWriteFile()