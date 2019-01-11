# coding=utf-8
from db.engine_factory import EngineFactory
from py2neo import Graph
from db.model import EntityForQA

class Neo4j2MySQL:
    @staticmethod
    def build_table():
        session = EngineFactory.create_session()
        # 慎重清表#
        # EntityForQA.clear_table(session)
        sql_list=["MATCH (n:api) RETURN id(n),n",
                  "MATCH(n:wikidata) RETURN id(n), n",
            "MATCH (n:`domain entity`) RETURN id(n), n.`domain_entity:name`,n.domain_entity_id"]
        label_list=["api","wikidata","domain entity"]

        for str, la in zip(sql_list, label_list):
            Neo4j2MySQL.neo4j_to_db(session, str, la)

    @staticmethod
    def judge_pure_english(keyword):
        return all(c >= u'\u0020' and c <= u'\u007e' for c in keyword)

    @staticmethod
    def match_and_insert_WikiData(session, kg_id, label,key, value,  value_list):
        find_list = ["description", "label", "name", "aliases", "declaration"]
        if Neo4j2MySQL.judge_pure_english(value) == True:
            for j in find_list:
                flag = key.find(j)
                if flag != -1 and value not in value_list:
                    entity = EntityForQA(kg_id=kg_id,entity_id=None,source=label,attr=key,
                                          attr_value=value)
                    session.add(entity)
                    value_list.append(value)
                    return value_list

    @staticmethod
    def match_and_insert_Api(session,kg_id, entity_id, label, key, value,  value_list):
        find_list = [ "name",  "declaration"]
        for j in find_list:
            flag = key.find(j)
            if flag != -1 and value not in value_list and len(value)!=0:
                entity = EntityForQA(kg_id=kg_id, entity_id=entity_id,source=label,
                                      attr=key, attr_value=value)
                session.add(entity)
                value_list.append(value)
                return value_list

    @staticmethod
    def neo4j_to_db(session,strsql,label):
        test_graph = Graph(
            "http://10.131.252.160:7474/browser/",
            username="neo4j",
            password="123456"
        )
        print("searching "+label)
        result = test_graph.run(strsql).data()
        print("get node info!")
        if label == "wikidata":
            for r in result:
                r_attr = r['n'].keys()
                kg_id = r['id(n)']
                value_list=[]
                for i in r_attr:
                    value = r['n'][i]
                    #整数不能判断纯英文，会出现编码问题
                    if isinstance(value, int):
                        continue
                    elif isinstance(value, list):
                        value = ' '.join(r['n'][i])
                    Neo4j2MySQL.match_and_insert_WikiData(session, kg_id, label,i, value,value_list)
            session.commit()
        elif label == "api":
            for r in result:
                r_attr = r['n'].keys()
                kg_id = r['id(n)']
                entity_id=r['n']['api_id']
                value_list=[]
                for i in r_attr:
                    Neo4j2MySQL.match_and_insert_Api(session, kg_id, entity_id, label,i, r['n'][i], value_list)
            session.commit()
        else:
            for r in result:
                entity = EntityForQA(kg_id=r['id(n)'], entity_id=r['n.domain_entity_id'],source=label,
                                      attr='domain_entity:name',attr_value=r['n.`domain_entity:name`'])
                session.add(entity)
            session.commit()

# if __name__=="__main__":
#     a=Neo4j2MySQL()
#     a.build_table()

