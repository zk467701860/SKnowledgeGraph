# -*- coding:utf8 -*-
import re
import string
import MySQLdb
import nltk

print 'begin load NormalizeUtil'
try:
    conn = MySQLdb.connect(host='10.141.221.73', user='root', passwd='root', port=3306, db='codehub',
                           charset='utf8')
    cur = conn.cursor()
except MySQLdb.Error, e:
    print "Mysql connection Error %d: %s" % (e.args[0], e.args[1])

entity_dict = {}
with open('data/id-entity.tsv', 'r') as fread:
    for line in fread:
        content = line.split('\t')
        entity_dict[content[1][:-1]] = 1
stop_word_list = nltk.corpus.stopwords.words('english')
wrong_word_dict = {}
for word in stop_word_list:
    wrong_word_dict[word] = 1
del stop_word_list
special_word_list = ['call','return','error','exception','class','method','field','package','interface','another','one','two','three','four','five','six','seven','eight','nine','ten','looking','documentation']
for word in special_word_list:
    wrong_word_dict[word] = 1
del special_word_list

def transform_url_to_qualifier(url):
    if url.endswith(']'):
        return ''
    if '//' in url:
        prefix = url[0:url.index('//') + 2]
        post_fix = url[url.index('//') + 2:]
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
            new_entity_id = ''
            for i in range(0, begin_index - count):
                new_entity_id += entity_list[i] + '/'
            for i in range(begin_index + count, len(entity_list)):
                new_entity_id += entity_list[i] + '/'
            new_entity_id = new_entity_id[:-1]
            url = prefix + new_entity_id
    if url.startswith('http://java.sun.com'):
        url = url.replace('http://java.sun.com', 'https://docs.oracle.com')
    if url.startswith('http') and not url.startswith('https'):
        url = url.replace('http', 'https')
    if 'index.html?' in url:
        url = url.replace('index.html?', '')
    if '.package-summary' in url:
        url = url.replace('.package-summary', '')
    url = url.replace('%20', ' ').replace('%3C', '<').replace('%3E', '>').replace('%28', '(').replace('%29', ')')
    qualifier = ''
    if url.startswith('https://developer.android.com/intl/'):
        url_list = url[35:].split('/')
        new_url = url[0:30]
        for i in range(1, len(url_list)):
            new_url += url_list[i] + '/'
        new_url = new_url[:-1]
        url = new_url
    if url.startswith('https://docs.oracle.com/javase/8/docs/api/'):
        url_list = url[42:].split('/')
        for i in range(0, len(url_list) - 1):
            qualifier += url_list[i] + '.'
        if '#' not in url_list[-1]:
            qualifier += url_list[-1][:-5]
        else:
            qualifier += url_list[-1][:url_list[-1].index('#') - 4]
            post_fix = url_list[-1][url_list[-1].index('#') + 1:]
            count = post_fix.count('-')
            if count == 0:
                qualifier += post_fix
            else:
                for i in range(0, count):
                    if i == 0:
                        post_fix = post_fix.replace('-', '(', 1)
                    elif i == count - 1:
                        post_fix = post_fix.replace('-', ')', 1)
                    else:
                        post_fix = post_fix.replace('-', ', ', 1)
                qualifier += post_fix
    elif url.startswith('https://docs.oracle.com/javase/6/docs/api/') or url.startswith('https://docs.oracle.com/javase/7/docs/api/'):
        url_list = url[42:].split('/')
        for i in range(0, len(url_list) - 1):
            qualifier += url_list[i] + '.'
        if '#' not in url_list[-1]:
            qualifier += url_list[-1][:-5]
        else:
            qualifier += url_list[-1][:url_list[-1].index('#') - 4]
            post_fix = url_list[-1][url_list[-1].index('#') + 1:]
            qualifier += post_fix
    elif url.startswith('https://developer.android.com/reference/') or url.startswith(
            'https://developers.google.cn/android/reference/'):
        if url.startswith('https://developer.android.com/reference/'):
            url_list = url[40:].split('/')
        else:
            url_list = url[47:].split('/')
        for i in range(0, len(url_list) - 1):
            qualifier += url_list[i] + '.'
        if '#' not in url_list[-1]:
            qualifier += url_list[-1][:-5]
        else:
            qualifier += url_list[-1][:url_list[-1].index('#') - 4]
            post_fix = url_list[-1][url_list[-1].index('#') + 1:]
            qualifier += post_fix
    else:
        return ''
    qualifier = qualifier.replace(' ', '')
    if qualifier.startswith('?') :
        qualifier = qualifier.replace('?', '')
    #print qualifier
    entity_id = ''
    try:
        sql = 'SELECT * FROM java_all_api_entity where qualified_name = \'%s\'' % (qualifier)
        cur.execute(sql)
        data = cur.fetchone()
        if data is not None or '(' in qualifier:
            if data is not None:
                entity_id = str(data[0])
                #print 'yes'
            else :
                prefix = qualifier[:qualifier.index('(')]
                postfix = qualifier[qualifier.index('(') + 1: -1]
                parameter_list = postfix.split(',')
                sql = "SELECT id,qualified_name FROM java_all_api_entity where qualified_name like '%" + prefix + "%'"
                cur.execute(sql)
                data = cur.fetchall()
                if data != ():
                    maxIndex = -1
                    maxCount = 0
                    entity_id = 0
                    for i in range(0, len(data)):
                        count = 0
                        data_parameter_list = data[i][1][qualifier.index('(') + 1: -1].split(',')
                        if len(parameter_list) == len(data_parameter_list):
                            for parameter in parameter_list:
                                if parameter in data[i][1]:
                                    count += 1
                            if count > maxCount:
                                maxCount = count
                                maxIndex = i
                                entity_id = str(data[i][0])
                    if maxIndex != -1:
                        qualifier = data[maxIndex][1]
                    else:
                        qualifier = ''
    except Exception as e:
        print('MySQL: %s   error:%s' % (sql, e))
    if qualifier != '' and entity_id in entity_dict:
        return qualifier
    return ''

def isLegalAlias(alias):
    if '(' not in alias and len(alias.split()) > 7:
        return ''
    elif '//' in alias:
        return ''
    utf8_pattern = re.compile(r'\\u[0-9a-zA-Z]+')
    alias = utf8_pattern.sub('', alias)
    punct_pattern = re.compile(r'[\\’!"#$%&\'\+\-/:;=@^`{|}~]+')
    alias = punct_pattern.sub('', alias)
    punct_pattern = re.compile('\s{2,}')
    alias = punct_pattern.sub(' ', alias)
    words = alias.split()
    begin_index = len(words)
    end_index = len(words) - 1
    for i in range(0, len(words)):
        if words[i].lower() not in wrong_word_dict:
            begin_index = i
            break
    for i in range(len(words) - 1, begin_index - 1, -1):
        if words[i].lower() not in wrong_word_dict:
            end_index = i
            break
    new_alias = ''
    for i in range(begin_index, end_index + 1):
        new_alias += words[i] + ' '
    new_alias = new_alias.strip()
    if re.compile('[%s]' % re.escape(string.punctuation)).sub('', new_alias).strip() == '':
        return ''
    if new_alias.isdigit():
        return ''
    return new_alias

def isLegalMention(alias):
    if '(' not in alias and len(alias.split()) > 7:
        return ''
    elif '//' in alias:
        return ''
    utf8_pattern = re.compile(r'\\u[0-9a-zA-Z]+')
    alias = utf8_pattern.sub('', alias)
    punct_pattern = re.compile(r'[\\’!"#$%&\'+\-/:;=@^`{|}~]+')
    alias = punct_pattern.sub('', alias)
    punct_pattern = re.compile('\s{2,}')
    alias = punct_pattern.sub(' ', alias)
    if re.compile('[%s]' % re.escape(string.punctuation)).sub('', alias).strip() == '':
        return ''
    if alias.isdigit():
        return ''
    return alias.strip()

if __name__=="__main__":
    test_text = 'There is method 1'
    print isLegalAlias(test_text)
    print isLegalAlias(test_text) == ''
    #print isLegalAlias('asd joa vfas as')
    #print transform_url_to_qualifier('http://docs.oracle.com/javase/8/docs/api/java/util/Arrays.html#parallelSetAll-T:A-java.util.function.IntFunction-')