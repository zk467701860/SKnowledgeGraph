from py2neo import Graph
import random

from db.engine_factory import EngineFactory
from db.model import APIEntity, APIAlias
from db.search import GeneralConceptEntitySearcher
from skgraph.graph.accessor.factory import GraphFactory


class NodeFusionCheck:
    useless_alias_type_list = [
        APIAlias.ALIAS_TYPE_SIMPLE_NAME_WITH_TYPE,
        APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
        APIAlias.ALIAS_TYPE_SIMPLE_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE,
        APIAlias.ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
        APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE
    ]

    def __init__(self, graph=None):
        if isinstance(graph, Graph):
            self._graph = graph
        else:
            self._graph, _config = GraphFactory.create_from_default_config(server_number=4)

    def get_node_id_list(self, label_name):
        query="MATCH (n:`{param1}`)-[r]-(m:`wikidata`) RETURN id(n) AS id".format(param1=label_name)
        record_list = self._graph.run(query).data()
        id_list = []
        for item in record_list:
            id_list.append(item["id"])
        return id_list

    def get_node_by_id(self, id_num, label_name):
        #print(label_name)
        if label_name == "api method":
            name = "qualified_name"
        else:
            name = "domain_entity:name"
        full_des = "short_description"
        query = "MATCH (n:`{param1}`) WHERE ID(n)={param2} RETURN n".format(param1=label_name, param2=id_num)
        record_list = self._graph.run(query).data()
        if full_des not in record_list[0]["n"]:
            #print(record_list)
            return record_list[0]["n"][name], "#Null"
        return record_list[0]["n"][name], record_list[0]["n"][full_des]

    def get_sentence_related_to_node(self,id_num, label_name):
        query = "MATCH (n:`{param1}`)-[r]-(s:`sentence`) WHERE ID(n)={param2} RETURN s.sentence_text as text, id(s) as " \
                "kg_id".format(param1=label_name, param2=id_num)
        record_list = self._graph.data(query)
        # print(record_list)
        for sentence in record_list:
            sentence["text"] = sentence["text"].replace("#", "").replace(r"\n", " ").replace(r"\r", " ").encode('raw_unicode_escape')
        return record_list

    def get_wikidata_related_to_node(self, id_num, label_name):
        query = "MATCH (n:`{param1}`)-[r]-(s:`wikidata`) WHERE ID(n)={param2} RETURN s.name as name, id(s) as " \
                "kg_id, s.`site:enwiki` as url".format(param1=label_name, param2=id_num)
        record_list = self._graph.run(query).data()
        return record_list

    def is_valid(self, name, general_concept_searcher):
        domain_name_array = name.split(" ")
        if len(domain_name_array) == 1:
            return False
        temp = [0 for i in range(0, len(domain_name_array))]
        candidate_wiki_set = general_concept_searcher.search(name)
        for each in candidate_wiki_set:
            for i in range(0, len(domain_name_array)):
                if domain_name_array[i].lower() in each.name.lower():
                    temp[i] += 1
        if len(candidate_wiki_set) == 0:
            return False
        total = len(candidate_wiki_set)
        score_list = []
        for each in temp:
            score = each * 1.00 / total
            score_list.append(score)
        score_list = sorted(score_list, reverse=True)
        if (len(score_list) > 1 and score_list[0] > 0.9) or score_list[-1] == 0.0:
            return False
        return True

    def api_is_valid(self, name, general_concept_searcher, session):
        api_entity = APIEntity.find_by_qualifier(session, name)
        all_aliases = api_entity.all_aliases
        useful_alias_list = set([])
        for alias_entity in all_aliases:
            if alias_entity.type in self.useless_alias_type_list:
                continue
            if api_entity.api_type == APIEntity.API_TYPE_METHOD or api_entity.api_type == APIEntity.API_TYPE_CONSTRUCTOR:
                if alias_entity.type == APIAlias.ALIAS_TYPE_QUALIFIER_NAME:
                    method_alias_need_to_add = alias_entity.alias.split("(")[0]
                    useful_alias_list.add(method_alias_need_to_add)
                    continue
            useful_alias_list.add(alias_entity.alias)
        if len(useful_alias_list) == 0:
            return False
        valid_count = 0
        for name in useful_alias_list:
            if self.is_valid(name, general_concept_searcher):
                valid_count += 1
        if valid_count * 1.0 / len(useful_alias_list) < 0.2:
            return False
        return True

    def get_test_node(self, label_name):
        temp_id_list = self.get_node_id_list(label_name)
        node_num = 0
        id_list = []
        while node_num < 500:
            example = random.sample(temp_id_list, 700)
            for id_num in example:
                name, des = self.get_node_by_id(id_num, label_name)
                if label_name == "domain entity":
                    sentence = self.get_sentence_related_to_node(id_num, label_name)
                    if len(sentence) == 0:
                        print(id_num)
                        continue
                elif name.endswith("(E)") or des == "#Null":
                    continue
                id_list.append(id_num)
            node_num = len(example)

        id_list = id_list

        session = EngineFactory.create_session()
        general_concept_searcher = GeneralConceptEntitySearcher(session)
        node_list = []
        for item in id_list:
            dic = {}
            dic["name"], full_des = self.get_node_by_id(item, label_name)
            dic["id"] = item
            dic["node_type"] = label_name

            # if not self.is_valid(dic['name'], general_concept_searcher):
            #     continue
            if not self.api_is_valid(dic["name"],general_concept_searcher, session):
                continue

            if label_name == "domain entity":
                dic["sentence"] = self.get_sentence_related_to_node(item, label_name)
                if len(dic["sentence"]) == 0:
                    continue
            else:
                dic["sentence"] = full_des.replace("#", "").replace("\r", "").replace("\n", "").encode("raw_unicode_escape")
            dic["related_wiki"] = self.get_wikidata_related_to_node(item, label_name)
            node_list.append(dic)
        return node_list

    @staticmethod
    def dict_to_string(dict_list):
        lines = []
        for item in dict_list:
            base_line = "#".join([str(item["id"]), item["name"].encode("raw_unicode_escape"), item["node_type"], str(item["sentence"])])
            for wiki in item["related_wiki"]:
                if not wiki["name"]:
                    wiki["name"] = "#Null"
                    continue
                if not wiki["url"]:
                    continue
                line = "#".join([base_line, str(wiki["kg_id"]), wiki["name"].encode('raw_unicode_escape'), wiki["url"].encode('raw_unicode_escape')])
                lines.append(line)
        return lines


if __name__ == "__main__":
    test = NodeFusionCheck()
    file_path = "test_node.txt"
    node_list_1 = test.get_test_node("api method")[:50]
    # node_list_2 = test.get_test_node("domain entity")[:50]
    print(node_list_1)
    # print(node_list_2)
    # lines = test.dict_to_string(node_list_1) + test.dict_to_string(node_list_2)
    lines = test.dict_to_string(node_list_1)
    print(lines)
    with open(file_path, "w") as f:
        for line in lines:
            f.write(line + "\n")
