# -*- coding:utf8 -*-

import sys
import nltk
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor

reload(sys)
sys.setdefaultencoding('utf8')

graph_client = GraphClient(server_number=1)
graph_accessor = DefaultGraphAccessor(graph_client)
'''
merge node and relation belong to extended knowledge and entity which name 
'''
class DuplicateCleaner:
    def merge_node(self):
        print 'begin merge node'
        query = "match(a:`extended knowledge`:entity) return id(a) as id,a.name as name"
        try:
            nodeList = []
            result = graph_accessor.graph.run(query)
            for n in result:
                node = (n['id'],n['name'])
                nodeList.append(node)
        except Exception:
            print 'wrond 1'
            exit(1)
            return []
        nodeDict = {}
        for n in nodeList:
            #print 'index  ' + str(a)
            if n[1] not in nodeDict:
                nodeDict[n[1]] = [n[0]]
            else:
                temp_list = nodeDict[n[1]]
                temp_list.append(n[0])
                nodeDict[n[1]] = temp_list
            #print nodedict
            #print 'len  ' + str(len(nodeDict))
        if len(nodeDict) < len(nodeList):
            count = 0
            total = 0
            for node_name in nodeDict:
                # print 'total  %d' % (total)
                if len(nodeDict[node_name]) > 1:
                    print 'count  %d, merge %d ' % (count, len(nodeDict[node_name]))
                    # print node_name + '   ' + str(nodedict[node_name])
                    query = 'match (a) where ID(a) in ' + str(nodeDict[
                                                                  node_name]) + ' with collect(a) as nodes\n CALL apoc.refactor.mergeNodes(nodes)\n YIELD node RETURN node'
                    try:
                        graph_accessor.graph.evaluate(query)
                    except Exception, error:
                        print 'name:  ' + node_name
                        print 'id:  ' + str(nodeDict[node_name])
                        print 'merge fail'
                    count += 1
                total += 1
        #self.merge_relation_with_same_label()
        print 'finish merge node'

    def clean_node(self):
        stop_word_list = list(set(nltk.corpus.stopwords.words('english')))
        print 'begin clean node'
        query = "match(a:`extended knowledge`:entity) return id(a) as id,a.name as name"
        nodeList = []
        try:
            result = graph_accessor.graph.run(query)
            for n in result:
                node = (n['id'], n['name'])
                nodeList.append(node)
        except Exception:
            print 'wrond 2'
            exit(2)
            return []
        print 'Before delete node name count:  %d' % (len(nodeList))
        print 'begin delete node'
        index = 1
        for n in nodeList:
            #print index
            node_name = n[1]
            is_delete = False
            if type(node_name) == unicode:
                if not node_name[0:1].isalpha():
                    is_delete = True
                else:
                    if not ' ' in node_name:
                        if node_name.lower() in stop_word_list:
                            is_delete = True
                        elif len(node_name) < 3 or (len(node_name) > 15 and '.' not in node_name and '(' not in node_name):
                            is_delete = True
                    else:
                        word_list = node_name.split(' ')
                        for i in range(0, len(word_list)):
                            if word_list[i].lower() not in stop_word_list:
                                if not word_list[i][0:1].isalpha():
                                    is_delete = True
                                break
                            if i == len(word_list) - 1:
                                is_delete = True
            else:
                is_delete = True
            if is_delete:
                print index
                print "begin delete node name:  %s" % (node_name)
                delete_out_relation_query = 'match (a:`extended knowledge`:entity)-[n]->(b) where id(a)={node_id} delete n'
                delete_in_relation_query = 'match (a:`extended knowledge`:entity)<-[n]-(b) where id(a)={node_id} delete n'
                delete_node_query = 'match (a:`extended knowledge`:entity) where id(a)={node_id} delete a'
                delete_out_relation_query = delete_out_relation_query.format(node_id=n[0])
                delete_in_relation_query = delete_in_relation_query.format(node_id=n[0])
                delete_node_query = delete_node_query.format(node_id=n[0])
                print "finish delete node name:  %s" % (node_name)
                try:
                    graph_accessor.graph.run(delete_out_relation_query)
                except Exception:
                    print delete_out_relation_query
                try:
                    graph_accessor.graph.run(delete_in_relation_query)
                except Exception:
                    print delete_in_relation_query
                try:
                    graph_accessor.graph.evaluate(delete_node_query)
                except Exception:
                    print delete_node_query
            index += 1
        print 'finish delete node'
        query = "match(a:`extended knowledge`:entity) return id(a) as id,a.name as name"
        nodeList = []
        node_name_list = []
        try:
            result = graph_accessor.graph.run(query)
            for n in result:
                node = (n['id'], n['name'])
                nodeList.append(node)
                node_name_list.append(n['name'])
        except Exception:
            print 'wrond 3'
            exit(3)
            return []
        print 'After delete node name count:  %d' % (len(nodeList))
        print 'begin change node'
        porter = nltk.stem.WordNetLemmatizer()
        index = 1
        for n in nodeList:
            #print index
            new_name = n[1]
            word_list = new_name.split(' ')
            formal_index = 0
            for i in range(0, len(word_list)):
                if word_list[i].lower() not in stop_word_list:
                    formal_index = i
                    break
            if formal_index > 0:
                new_name = ''
                for i in range(formal_index, len(word_list)):
                    new_name += word_list[i] + ' '
                new_name = new_name[:-1]
            lower_name = new_name.lower()
            word_lower_list = nltk.word_tokenize(lower_name)
            lemma_lower_list = []
            for i in range(0, len(word_lower_list)):
                word = word_lower_list[i]
                if word.endswith("ing") or word.endswith("ed") or word.endswith("es") or word.endswith(
                        "ies") or word.endswith("s"):
                    lemma_lower_list.append(porter.lemmatize(word, "v"))
                elif word.endswith("er") or word.endswith("est"):
                    lemma_lower_list.append(porter.lemmatize(word, "a"))
                else:
                    lemma_lower_list.append(porter.lemmatize(word, "n"))
            lemma_lower_name = ''
            for word in lemma_lower_list:
                lemma_lower_name += word + " "
            lemma_lower_name = lemma_lower_name[:-1]
            query = "match (a:`extended knowledge`:entity) where id(a)={node_id} set a.name = '{new_name}'"
            if lemma_lower_name in node_name_list:
                new_name = lemma_lower_name
            if n[1] != new_name:
                new_name = new_name.replace("'", "\\\'")
                query = query.format(node_id=n[0], new_name=new_name)
                #graph_accessor.graph.run(query)
                try:
                    graph_accessor.graph.run(query)
                    print index
                    print "%s  ->  %s" % (n[1], new_name)
                except Exception:
                    print query
            index += 1
        print 'finish change node'

    def merge_relation(self):
        print 'begin merge relation'
        query = 'CALL db.relationshipTypes()'
        relationList = []
        try:
            result = graph_accessor.graph.run(query)
            for n in result:
                relationList.append(n['relationshipType'])
        except Exception:
            print 'wrond 4'
            exit(4)
            return []
        print 'relation type count:  %s' %(str(len(relationList)))
        relationCount = len(relationList)
        for i in range(0, relationCount):
            print 'start merge relation:  %d,type:  %s' %(i+1, relationList[i])
            query = 'match(a:entity)-[n:`{label}`]->(b:entity) return id(a) as start,id(n) as rel,id(b) as end'
            relation_label = relationList[i].replace('`','``')
            query = query.format(label=relation_label)
            relationDict = {}
            try:
                result = graph_accessor.graph.run(query)
            except Exception:
                print 'wrong parameter %s' % (query)
            #count = 0
            for n in result:
                dictKey = str(n['start']) + '#' + str(n['end'])
                if dictKey not in relationDict:
                    relationDict[dictKey] = [n['rel']]
                else:
                    temp_list = relationDict[dictKey]
                    temp_list.append(n['rel'])
                    relationDict[dictKey] = temp_list
                #count += 1
            # print 'count:  %d, dict length:  %d' %(count, len(relationDict))
            for key in relationDict:
                if len(relationDict[key]) > 1:
                    print ('relation: %s, key: %s, number:  %d') %(relation_label, key, len(relationDict[
                                                                         key]))
                    query = 'match ()-[n]->() where ID(n) in ' + str(relationDict[
                                                                         key]) + ' with collect(n) as relations\n CALL apoc.refactor.mergeRelationships(relations)\n YIELD rel RETURN rel'
                    try:
                        graph_accessor.graph.evaluate(query)
                    except Exception:
                        print query

    def clean_relation(self):
        print 'begin clean relation'
        illegal_character_list = [".","*",","]
        query = 'CALL db.relationshipTypes()'
        relation_list = []
        try:
            result = graph_accessor.graph.run(query)
        except Exception:
            print query
        for n in result:
            relation_list.append(str(n['relationshipType']))
        relation_list = sorted(relation_list, key=str.lower)
        print 'begin delete relation'
        print 'Before delete relation label count:  %d' % (len(relation_list))
        index = 1
        for relation in relation_list:
            #print index
            is_delete = False
            if relation[0:1].isalpha():
                if '(' in relation or ')' in relation:
                    is_delete = True
                elif 'wheel' not in relation and (relation.startswith('wh') or relation.startswith('Wh') or relation.startswith('WH')):
                    is_delete = True
                else:
                    for character in illegal_character_list:
                        if character in relation:
                            is_delete = True
                            break
            else:
                if not relation.startswith("'ll") and not relation.startswith("'s been"):
                    is_delete = True
            if is_delete:
                print index
                print "delete relation label:  %s" %(relation)
                query = 'match (a:entity)-[r:`{label}`]->(b:entity) delete r'
                relation_label = relation.replace('`', '``')
                query = query.format(label=relation_label)
                try:
                    graph_accessor.graph.run(query)
                except Exception:
                    print query
            index += 1
        print "finish delete relation"
        query = 'CALL db.relationshipTypes()'
        relation_list = []
        try:
            result = graph_accessor.graph.run(query)
        except Exception:
            print query
        for n in result:
            relation_list.append(str(n['relationshipType']))
        relation_list = sorted(relation_list, key=str.lower)
        porter = nltk.stem.WordNetLemmatizer()
        print 'After delete relation label count:  %d' % (len(relation_list))
        print "begin change relation"
        index = 1
        for relation in relation_list:
            #print index
            new_label = relation
            # 判断开头字母是否非法
            if relation[0:1].isalpha():
                if 'is is' in relation:
                    new_label = relation.replace('is is', 'is')
                if "n't" in relation:
                    if "ca n't" in relation:
                        new_label = relation.replace("ca n't", "can not")
                    elif "wo n't" in relation:
                        new_label = relation.replace("wo n't", "will not")
                    else:
                        new_label = relation.replace("n't", "not")
                if 'might' in relation:
                    new_label = relation.replace("might", "may",1)
                if 'could' in relation:
                    new_label = relation.replace("could", "can",1)
                if 'would' in relation:
                    new_label = relation.replace("would", "will",1)
                if 'did' in relation:
                    new_label = relation.replace("did", "do",1)
                if 'does' in relation:
                    new_label = relation.replace("does", "do",1)
                if relation.startswith('is '):
                    new_label = relation.replace("is ", "",1)
                if relation.startswith('are '):
                    new_label = relation.replace("are ", "",1)
                if relation.startswith('was '):
                    new_label = relation.replace("was ", "",1)
                if relation.startswith('were '):
                    new_label = relation.replace("were ", "",1)
                if relation.startswith('have'):
                    new_label = relation.replace("have", "has",1)
                if relation.startswith('do ') and not relation.startswith('do not'):
                    new_label = relation.replace("do ", "", 1)
            else:
                if relation.startswith("'ll"):
                    new_label = relation.replace("'ll", "will")
                elif relation.startswith("'s been"):
                    new_label = relation.replace("'s been", "been")
            lower_label = new_label.lower()
            word_lower_list = nltk.word_tokenize(lower_label)
            lemma_lower_list = []
            for word in word_lower_list:
                if word.endswith("ing") or word.endswith("ed") or word.endswith("es") or word.endswith(
                        "ies") or word.endswith("s"):
                    lemma_lower_list.append(porter.lemmatize(word, "v"))
                elif word.endswith("er") or word.endswith("est"):
                    lemma_lower_list.append(porter.lemmatize(word, "a"))
                else:
                    lemma_lower_list.append(porter.lemmatize(word, "n"))
            lemma_lower_label = ''
            for word in lemma_lower_list:
                lemma_lower_label += word + " "
            lemma_lower_label = lemma_lower_label[:-1]
            query = 'match (n:entity)-[r:`{label}`]->(m:entity) create (n)-[r2:`{newLabel}`]->(m) set r2 = r with r delete r'
            relation_label = relation.replace('`', '``')
            if lemma_lower_label in relation_list:
                new_label = lemma_lower_label.replace('`', '``')
            else:
                new_label = new_label.replace('`', '``')
            if relation_label != new_label:
                query = query.format(label=relation_label, newLabel=new_label)
                try:
                    print index
                    graph_accessor.graph.run(query)
                    print "%s  ->  %s" % (relation, new_label)
                except Exception:
                    print query
            index += 1
        print 'finish change relation'
        #self.merge_relation()

if __name__ == '__main__':
    cleaner = DuplicateCleaner()
    cleaner.clean_node()
    cleaner.merge_node()
    cleaner.clean_relation()
    cleaner.merge_relation()