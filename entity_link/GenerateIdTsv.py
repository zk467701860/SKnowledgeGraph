import MySQLdb
import sys
from gensim.models import KeyedVectors

reload(sys)
sys.setdefaultencoding('utf8')

def generate():
    gragh_wv = KeyedVectors.load_word2vec_format("data/graph embedding/graph_output.emb", binary=False)
    gragh_vocab = set(gragh_wv.vocab.keys())
    print len(gragh_vocab)
    entity_wv = KeyedVectors.load_word2vec_format("data/word embedding/entity-vector.txt", binary=False)
    entity_vocab = set(entity_wv.vocab.keys())
    print len(entity_vocab)
    id_set = gragh_vocab.intersection(entity_vocab)
    print len(id_set)
    try:
        conn = MySQLdb.connect(host='10.141.221.73', user='root', passwd='root', port=3306, db='codehub',
                               charset='utf8')
        cur = conn.cursor()
    except MySQLdb.Error, e:
        print "Mysql connection Error %d: %s" % (e.args[0], e.args[1])
    id_entity_pair = {}
    try:
        sql = 'select id,qualified_name FROM java_all_api_entity'
        cur.execute(sql)
        data = cur.fetchall()
        if data != ():
            for entity in data:
                id_entity_pair[str(entity[0])] = entity[1]
    except Exception as e:
        conn.rollback()
        print('MySQL: %s   error:%s' % (sql, e))
    id_entity_tsv = open('data/id-entity.tsv', 'w')
    for entity_id in id_set:
        id_entity_tsv.writelines('%s\t%d\n' % (id_entity_pair[entity_id], int(entity_id)))
    id_entity_tsv.close()

if __name__ == '__main__':
    generate()