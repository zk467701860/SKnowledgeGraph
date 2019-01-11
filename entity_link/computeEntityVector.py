# encoding: utf-8
from gensim.models import KeyedVectors
import MySQLdb
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
import sys

reload(sys)
sys.setdefaultencoding('utf8')

STRIP_STR = ' ’!"$%&\'()*,-./:;<=>?‘“”？，；…@[\\]^_`{|}~'
'''
#todo
def computeWithIDF(documents):
    print("Dictionary establish...")
    texts = []
    for doc in documents:
        words = doc.split()
        texts.append(words)
    dic = gensim.corpora.Dictionary(texts)
    dic.filter_extremes(no_below=1, no_above=1)
    dic.save("data/embedding/dict")
    print dic.token2id
    print("Dictionary end...")
    corpus_list = [dic.doc2bow(text) for text in texts]
    tfidfModel = gensim.models.TfidfModel(corpus=corpus_list, id2word={}, dictionary=dic)
    print tfidfModel.idfs.keys()
    print tfidfModel.idfs.values()
    print tfidfModel.idfs.get(dic.token2id['a'])
    print tfidfModel.idfs.get(dic.token2id['b'])
    print tfidfModel.idfs.get(dic.token2id['c'])
    print tfidfModel.idfs.get(dic.token2id['d'])
'''

def testVector():
    wv = KeyedVectors.load('data/word embedding/vocab.txt')
    vocab = set(wv.vocab.keys())
    text = 'java split'
    words = nltk.word_tokenize(text)
    lem = WordNetLemmatizer()
    print words
    count = 0
    entity_vec = np.zeros(128)
    f = open("data/word embedding/entity-vector.txt", 'w')
    for word in words:
        print word
        new_word = lem.lemmatize(word.lower().strip(STRIP_STR))
        print new_word
        if new_word in vocab:
            count += 1
            vec = wv[new_word]
            print vec
            entity_vec += np.array(vec)
    print count
    entity_vec /= count
    print entity_vec
    final_vec_string = ''
    vec_list = entity_vec.tolist()
    for dimension in vec_list:
        final_vec_string += str(dimension) + ' '
    final_vec_string = final_vec_string[:-1]
    api = 180
    print final_vec_string
    f.writelines('%d %s' % (api, final_vec_string))
    f.close()

def computeWithAverage():
    try:
        conn = MySQLdb.connect(host='10.141.221.73', user='root', passwd='root', port=3306, db='codehub',
                               charset='utf8')
        cur = conn.cursor()
    except MySQLdb.Error, e:
        print "Mysql connection Error %d: %s" % (e.args[0], e.args[1])
    f = open("data/word embedding/entity-vector.txt", 'w')
    wv = KeyedVectors.load('data/word embedding/vocab.txt')
    vocab = set(wv.vocab.keys())
    lem = WordNetLemmatizer()
    index = 0
    try:
        sql = 'select api_id, clean_text from java_api_html_text where id in (select min(id) from java_api_html_text where html_type = 3 group by api_id)'
        cur.execute(sql)
        data = cur.fetchall()
    except Exception as e:
        conn.rollback()
        print('MySQL: %s   error:%s' % (sql, e))
    if data != ():
        print 'total entity number: %d' % (len(data))
        for content in data:
            #print index
            api = content[0]
            text = content[1]
            words = nltk.word_tokenize(text)
            count = 0
            entity_vec = np.zeros(128)
            for word in words:
                #print word
                new_word = lem.lemmatize(word.lower().strip(STRIP_STR))
                if new_word in vocab:
                    count += 1
                    vec = wv[new_word]
                    entity_vec += np.array(vec)
            if count != 0:
                entity_vec /= count
                final_vec_string = ''
                vec_list = entity_vec.tolist()
                for dimension in vec_list:
                    final_vec_string += str(dimension) + ' '
                final_vec_string = final_vec_string[:-1]
                f.writelines('%d %s\n' % (api, final_vec_string))
            else:
                print 'no correct word in %d' % (api)
            index += 1
            if index % 100 == 0:
                print 'finish %d' % (index)
    f.close()

def changeFileFormat():
    write_f = open('data/word embedding/entity-vector1.txt', 'w')
    with open('data/word embedding/entity-vector.txt', 'r') as load_f:
        index = 0
        for line in load_f:
            item = line.split('\t')
            write_f.writelines('%s %s' % (item[0], item[1]))
            index += 1
            if index % 100 == 0:
                print index
    write_f.close()

if __name__ == "__main__":
    '''
    traindata = "data/embedding/test.json"
    with open(traindata, "r",) as f:
        document = json.load(f)
        '''
    computeWithAverage()
    #testVector()
    #changeFileFormat()
