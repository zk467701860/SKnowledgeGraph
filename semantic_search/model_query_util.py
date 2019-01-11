import time

import numpy as np

from model_util.entity_vector.entity_vector_model import EntityVectorModel, EntityVectorComputeModel
from semantic_search.matrix_calculation import MatrixCalculation
from skgraph.graph.accessor.graph_accessor import GraphClient, DefaultGraphAccessor

np.seterr(divide='ignore', invalid='ignore')
MIN_RELATED_ENTITY_SIMILARITY = 0.80


class KnowledgeGraphFeafureModels:
    WORD2VEC_FILE_LIST = {"domain entity": "domain_entity.binary.txt",
                          "api": "api.binary.txt",
                          "wikidata": "wikipedia.binary.txt",
                          "sentence": "sentence.binary.txt",
                          "graph": "graph_vector.binary.txt",
                          "word2vec": "word2vec_api_software_wiki.txt"
                          }
    WORDVECTOR_KEY_MAP = {
        "domain entity": "domain_entity_id",
        "api": "api_id",
        "sentence": "sentence_id",
        "wikidata": "wd_kg_id"
    }

    def __init__(self):
        self._api_wv = None
        self._domain_entity_wv = None
        self._wiki_wv = None
        self._sentence_wv = None
        self._graph_wv = None
        self._entity_vector_compute_model = None
        self.NP_VECTOR_NOT_EXIST = None
        self.defaultAccessor = None

    def init(self, vector_dir_path="./model/", ):
        time_start = time.time()
        print("start init the model=%d" % time_start)
        client = GraphClient(server_number=4)

        self.defaultAccessor = DefaultGraphAccessor(client)

        self._api_wv = EntityVectorModel.load(vector_dir_path + self.WORD2VEC_FILE_LIST["api"], binary=True)
        self._domain_entity_wv = EntityVectorModel.load(vector_dir_path + self.WORD2VEC_FILE_LIST["domain entity"],
                                                        binary=True)
        self._wiki_wv = EntityVectorModel.load(vector_dir_path + self.WORD2VEC_FILE_LIST["wikidata"], binary=True)
        self._sentence_wv = EntityVectorModel.load(vector_dir_path + self.WORD2VEC_FILE_LIST["sentence"], binary=True)
        self._graph_wv = EntityVectorModel.load(vector_dir_path + self.WORD2VEC_FILE_LIST["graph"], binary=True)
        self._entity_vector_compute_model = EntityVectorComputeModel()
        self._entity_vector_compute_model.init_word2vec_model(vector_dir_path + self.WORD2VEC_FILE_LIST["word2vec"],
                                                              binary=True)
        self.NP_VECTOR_NOT_EXIST = np.zeros(128)
        self.NP_VECTOR_NOT_EXIST[1] = 1e-07

        time_end = time.time()
        print("init complete in %d" % (time_end - time_start))

    def get_entity_vec(self, entity_node):
        entity_type = ""
        wv_model = None
        if entity_node.has_label("wikidata"):
            entity_node["wd_kg_id"] = "kg#" + str(self.defaultAccessor.get_id_for_node(entity_node))
            entity_type = "wikidata"
            wv_model = self._wiki_wv
        if entity_node.has_label("sentence"):
            entity_type = "sentence"
            wv_model = self._sentence_wv

        if entity_node.has_label("domain entity"):
            entity_type = "domain entity"
            wv_model = self._domain_entity_wv

        if entity_node.has_label("api"):
            entity_type = "api"
            wv_model = self._api_wv

        if wv_model is None or entity_type is "":
            return self.NP_VECTOR_NOT_EXIST
        vector_key_name = self.WORDVECTOR_KEY_MAP[entity_type]

        word2vec_id_string = str(entity_node[vector_key_name])
        if word2vec_id_string not in wv_model.vocab:
            return self.NP_VECTOR_NOT_EXIST

        return wv_model[word2vec_id_string]

    def get_question_entity_vector(self, question):
        question_vec = self._entity_vector_compute_model.compute_mean_vector(question, need_process=True)
        return question_vec

    def get_question_graph_vector_by_average_all_entities(self, question, entity_graph_vec_list):
        question_graph_vec = np.mean(entity_graph_vec_list, axis=0)
        return question_graph_vec

    def get_question_graph_vector_by_semantic_weight_all_entities(self, question_context_vec, entity_context_vec_list,
                                                                  entity_graph_vec_list):
        qe_sim_np = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                 entity_context_vec_list)
        qe_sim_np = qe_sim_np / qe_sim_np.sum()

        question_graph_vec = (qe_sim_np * np.matrix(entity_graph_vec_list)).getA()[0]
        return question_graph_vec

    def get_vectors_for_entity_list(self, entity_list):
        entity_graph_vec_list = []
        entity_vec_list = []
        for entity in entity_list:
            entity_vec_list.append(self.get_entity_vec(entity))
            entity_graph_vec_list.append(self.get_entity_graph_vec(entity))
        return entity_vec_list, entity_graph_vec_list

    def get_entity_graph_vec(self, entity):
        wv_model = self._graph_wv
        word2vec_id_string = str(self.defaultAccessor.get_id_for_node(entity))
        if word2vec_id_string not in wv_model.vocab:
            return self.NP_VECTOR_NOT_EXIST

        return wv_model[word2vec_id_string]


class NodeInfoCollection:
    def __init__(self):
        self.node_info_list = []

    def add(self, node_info):
        if node_info is None:
            return
        self.node_info_list.append(node_info)

    def get_entity_list(self):
        return [info.entity_node for info in self.node_info_list]

    def get_entity_graph_list(self):
        return [info.entity_graph_vec for info in self.node_info_list]

    def get_entity_context_list(self):
        return [info.entity_context_vec for info in self.node_info_list]

    def get_all_node_infos(self):
        return self.node_info_list

    def __repr__(self):
        return str(self.node_info_list)

    def size(self):
        return len(self.node_info_list)

    def print_info(self):
        for index, node_info in enumerate(self.node_info_list):
            print("entity", index, node_info)

    def init_vectors(self, kg_models):
        for node_info in self.node_info_list:
            entity_node = node_info.get_entity_node()
            node_info.entity_context_vec = kg_models.get_entity_vec(entity_node)
            node_info.entity_graph_vec = kg_models.get_entity_graph_vec(entity_node)

    def fill_each_entity_with_similary_to_question(self, question_context_vec):
        entity_context_vec_list = self.get_entity_context_list()
        qe_sim_np = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                 entity_context_vec_list)

        for entity_info, sim in zip(self.node_info_list, qe_sim_np.getA()[0]):
            entity_info.qe_sim = sim

    def sort_by_qe_sim(self):
        self.node_info_list.sort(key=lambda k: (k.qe_sim), reverse=True)

    def get_first_match_entity_for_qa(self, entity_for_qa_list):
        for node_info in self.node_info_list:
            for entity_for_qa in entity_for_qa_list:
                if entity_for_qa in node_info.entity_for_qa_list:
                    return node_info

    def get_first_match_entity_for_qa_for_three_type_entity(self, entity_for_qa_list):
        entity_for_qa_list_for_api = []
        entity_for_qa_list_for_domain_entity = []
        entity_for_qa_list_for_wikidata = []

        for entity_for_qa in entity_for_qa_list:
            if entity_for_qa.source == "api":
                entity_for_qa_list_for_api.append(entity_for_qa)
            if entity_for_qa.source == "domain entity":
                entity_for_qa_list_for_domain_entity.append(entity_for_qa)
            if entity_for_qa.source == "wikidata":
                entity_for_qa_list_for_wikidata.append(entity_for_qa)

        node_info_list = []
        temp_node_info = []

        temp_node_info.append(self.get_first_match_entity_for_qa(entity_for_qa_list_for_api))
        temp_node_info.append(self.get_first_match_entity_for_qa(entity_for_qa_list_for_domain_entity))
        temp_node_info.append(self.get_first_match_entity_for_qa(entity_for_qa_list_for_wikidata))
        for t in temp_node_info:
            if t is not None:
                node_info_list.append(t)

        return node_info_list

    def remove_the_entity_by_qe_similarity(self):
        new_info_list = []
        if len(self.node_info_list) < 100:
            return

        for node_info in self.node_info_list:
            if node_info.qe_sim >= MIN_RELATED_ENTITY_SIMILARITY:
                new_info_list.append(node_info)
        self.node_info_list = new_info_list

    def get_node_kg_id_str_list(self):
        id_str_list = set([])
        for node_info in self.node_info_list:
            id_str_list.add(str(node_info.node_id))
        return list(id_str_list)


class NodeInfo:
    def __init__(self, entity_node, node_id, entity_for_qa_list=None):
        if entity_for_qa_list is None:
            entity_for_qa_list = set([])
        self.entity_for_qa_list = set(entity_for_qa_list)
        self.entity_node = entity_node
        self.node_id = node_id
        self.entity_graph_vec = None
        self.entity_context_vec = None
        self.qe_sim = 0

    def add_entity_for_qa(self, entity_for_qa):
        if entity_for_qa.kg_id == self.node_id:
            self.entity_for_qa_list.add(entity_for_qa)

    def __repr__(self):
        return "<NodeInfo qe_sim=%r entity_for_qa  =%r node=%r " % (
            self.qe_sim, self.entity_for_qa_list, self.entity_node)

    def get_entity_node(self):
        return self.entity_node

    def __hash__(self):
        return self.node_id

    def __eq__(self, other):
        # another object is equal to self, iff
        # it is an instance of MyClass
        return isinstance(other, NodeInfo)


class SentenceInfo:
    def __init__(self, sentence_node, node_id):
        self.sentence_node = sentence_node
        self.node_id = node_id
        self.sentence_graph_vec = None
        self.sentence_context_vec = None
        self.qs_sim = 0
        self.qs_graph_sim = 0
        self.qs_context_sim = 0

        self.api_id = None
        self.api_qualified_name = None
        self.api_kg_id = None
        self.api_type = None
        self.api_document_website = None

    def __repr__(self):
        return "<SentenceInfo=%r qs_sim=%r qs_graph_sim=%r qs_context_sim=%r api=%r node=%r  >" % (
            self.node_id, self.qs_sim, self.qs_graph_sim, self.qs_context_sim,
            self.api_qualified_name, self.sentence_node)

    def get_entity_node(self):
        return self.sentence_node

    def parse_to_json(self):
        return {
            "kg_id": self.node_id,
            "sentence_id": self.sentence_node["sentence_id"],
            "text": self.sentence_node["sentence_text"],
            "sentence_type": self.sentence_node["sentence_type_code"],
            "qs_sim": self.qs_sim,
            "qs_context_sim": self.qs_context_sim,
            "qs_graph_sim": self.qs_graph_sim,
            "api_id": self.api_id,
            "api_qualified_name": self.api_qualified_name,
            "api_kg_id": self.api_kg_id,
            "api_type": self.api_type,
            "api_document_website": self.api_document_website,
        }


class SentenceInfoCollection:
    SENTENCE_SIMLARITY_FILTER = 0.8

    def __init__(self):
        self.sentence_info_list = []

    def add(self, node_info):
        self.sentence_info_list.append(node_info)

    def add_sentence_node(self, sentence_node, node_id):
        self.sentence_info_list.append(SentenceInfo(sentence_node, node_id=node_id))

    def get_entity_list(self):
        return [info.sentence_node for info in self.sentence_info_list]

    def get_entity_graph_list(self):
        return [info.sentence_graph_vec for info in self.sentence_info_list]

    def get_entity_context_list(self):
        return [info.sentence_context_vec for info in self.sentence_info_list]

    def get_all_sentence_infos(self):
        return self.sentence_info_list

    def __repr__(self):
        return str(self.sentence_info_list)

    def size(self):
        return len(self.sentence_info_list)

    def print_info(self):
        for node_info in self.sentence_info_list:
            print(node_info)

    def init_vectors(self, kg_models):
        for node_info in self.sentence_info_list:
            entity_node = node_info.get_entity_node()
            node_info.sentence_context_vec = kg_models.get_entity_vec(entity_node)
            node_info.sentence_graph_vec = kg_models.get_entity_graph_vec(entity_node)

    def sort_by_qs_sim(self):
        self.sentence_info_list.sort(key=lambda k: (k.qs_sim), reverse=True)

    def get_top_n_json(self, top_n):
        result = []
        for sentence_info in self.sentence_info_list[:top_n]:
            result.append(sentence_info.parse_to_json())
        return result

    def get_all_as_json(self):
        result = []
        for sentence_info in self.sentence_info_list:
            result.append(sentence_info.parse_to_json())
        return result

    def get_top_n_as_sub_sentence_collection(self, top_n):
        collection = SentenceInfoCollection()
        for sentence_info in self.sentence_info_list[:top_n]:
            if sentence_info.qs_sim > self.SENTENCE_SIMLARITY_FILTER:
                collection.add(sentence_info)
        return collection

    def get_sum_qs_sim(self):
        qs_sim = 0
        for sentence_info in self.sentence_info_list:
            qs_sim = qs_sim + sentence_info.qs_sim
        return qs_sim

    def filter_others_sentences(self):
        new_sentence_info_list = []

        for sentence_info in self.sentence_info_list:
            if sentence_info.sentence_node["sentence_type_code"] != 0:
                new_sentence_info_list.append(sentence_info)

        self.sentence_info_list = new_sentence_info_list


class APIInfo:
    def __init__(self, api_node, node_id):
        self.api_node = api_node
        self.node_id = node_id
        self.graph_vec = None
        self.context_vec = None
        self.qe_context_sim = 0
        self.qe_graph_sim = 0
        self.qe_sim = 0

    def __repr__(self):
        return "<APIInfo=%r qe_sim=%r qe_graph_sim=%r qe_context_sim=%r node=%r >" % (
            self.node_id, self.qe_sim, self.qe_graph_sim, self.qe_context_sim, self.api_node)

    def get_entity_node(self):
        return self.api_node

    def __hash__(self):
        return self.node_id

    def __eq__(self, other):
        # another object is equal to self, iff
        # it is an instance of MyClass
        return isinstance(other, APIInfo)

    def get_url(self):
        return self.api_node["api_document_website#1"]

    def get_class_name(self):
        url = self.get_url()
        if url == None:
            return ""
        return url.split("#")[0].replace("https://developer.android.com/reference/", ""). \
            replace("https://developer.android.com/reference/", "").replace("http://docs.oracle.com/javase/8/docs/api/",
                                                                            "").replace(
            "http://docs.oracle.com/javase/7/docs/api/", "").replace("http://docs.oracle.com/javase/6/docs/api/",
                                                                     "").replace(
            "http://docs.oracle.com/javase/1.5.0/docs/api/", "").replace(".html", "").replace("/", ".")

    def get_quailified_name(self):
        return self.api_node["qualified_name"]


class APIInfoCollection:
    def __init__(self):
        self.api_info_list = []
        self.api_node_id_set = set([])

    def add(self, node_info):
        if node_info is None:
            return
        if node_info.node_id in self.api_node_id_set:
            return
        self.api_node_id_set.add(node_info.node_id)

        self.api_info_list.append(node_info)

    def init_vectors(self, kg_models):
        for api_node_info in self.api_info_list:
            entity_node = api_node_info.get_entity_node()
            api_node_info.context_vec = kg_models.get_entity_vec(entity_node)
            api_node_info.graph_vec = kg_models.get_entity_graph_vec(entity_node)

    def get_entity_list(self):
        return [info.api_node for info in self.api_info_list]

    def get_entity_graph_list(self):
        return [info.graph_vec for info in self.api_info_list]

    def get_entity_context_list(self):
        return [info.context_vec for info in self.api_info_list]

    def get_all_sentence_infos(self):
        return self.api_info_list

    def __repr__(self):
        return str(self.api_info_list)

    def size(self):
        return len(self.api_info_list)

    def print_info(self):
        for node_info in self.api_info_list:
            print(node_info)

    def filter_the_api_by_remove_package(self):
        new_info_list = []

        for api_info in self.api_info_list:
            if api_info.api_node["api type"] != 1 and api_info.api_node["api type"] != 14 and api_info.api_node[
                "api type"] != 15 and api_info.api_node["api type"] != 16:
                new_info_list.append(api_info)

        self.api_info_list = new_info_list

    def remove_the_entity_by_qe_similarity(self):
        new_info_list = []

        for api_info in self.api_info_list:
            if api_info.qe_sim >= MIN_RELATED_ENTITY_SIMILARITY:
                new_info_list.append(api_info)

        self.api_info_list = new_info_list

    def remove_the_entity_by_save_some_candidate(self, top_number=10000):
        self.api_info_list = self.api_info_list[:top_number]

    def fill_each_entity_with_similary_to_question(self, question_context_vec):
        entity_context_vec_list = self.get_entity_context_list()
        qe_sim_np = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                 entity_context_vec_list)

        for entity_info, sim in zip(self.api_info_list, qe_sim_np.getA()[0]):
            entity_info.qe_sim = sim

    def sort_by_qe_sim(self):
        self.api_info_list.sort(key=lambda k: (k.qe_sim), reverse=True)

    def get_node_kg_id_str_list(self):
        id_str_list = set([])
        for node_info in self.api_info_list:
            id_str_list.add(str(node_info.node_id))
        return list(id_str_list)

    def get_top_api_info_group_by_api_class(self, top=100):
        group = {

        }

        top_api_info_list = self.api_info_list[:top]
        for top_api_info in top_api_info_list:
            class_name = top_api_info.get_class_name()
            if class_name in group:
                group[class_name].append(top_api_info)
            else:
                group[class_name] = [top_api_info]

        if "" in group:
            group.pop("")
        return group


class QACacheInfoManager:
    def __init__(self, semanticSearchAccessor, defaultSearchAccessor, kg_models, echo=False):
        self.keyword_2_entitynodemap = {}
        self.semanticSearchAccessor = semanticSearchAccessor
        self.defaultSearchAccessor = defaultSearchAccessor
        self.all_entity_node_list = None
        self.start_entity_node_info_collection = NodeInfoCollection()
        self.sentence_info_collection = SentenceInfoCollection()
        self.kg_models = kg_models
        self.api_node_info_collection = APIInfoCollection()

        self.top_related_entity_info_collection = NodeInfoCollection()
        self.echo = False

    def add(self, search_key_word, entity_to_node_alias_map):
        if search_key_word not in self.keyword_2_entitynodemap:
            self.keyword_2_entitynodemap[search_key_word] = entity_to_node_alias_map
        else:
            self.keyword_2_entitynodemap[search_key_word].extend(entity_to_node_alias_map)

    def __repr__(self):
        return str(self.keyword_2_entitynodemap)

    def get_all_entity_for_qa_list(self):
        result_set = set([])
        for keyword, entity_for_qa_list in self.keyword_2_entitynodemap.items():
            for entity_for_qa in entity_for_qa_list:
                result_set.add(entity_for_qa)
        return result_set

    def start_create_node_info_collection(self):
        entity_qa_list = self.get_all_entity_for_qa_list()
        entity_id_string_list = [str(entity_for_qa.kg_id) for entity_for_qa in entity_qa_list]
        entity_id_string_list = list(set(entity_id_string_list))

        self.all_entity_node_list = self.semanticSearchAccessor.get_all_entity(
            entity_id_string_list=entity_id_string_list)

        self.start_entity_node_info_collection = NodeInfoCollection()
        for entity_node in self.all_entity_node_list:
            node_id = self.defaultSearchAccessor.get_id_for_node(entity_node)

            node_info = NodeInfo(entity_node=entity_node, node_id=node_id)
            for entity_qa in entity_qa_list:
                node_info.add_entity_for_qa(entity_qa)

            self.start_entity_node_info_collection.add(node_info)

    def get_top_node_info_by_each_keywords(self):
        result = set([])
        for (keyword, entity_fo_qa_list) in self.keyword_2_entitynodemap.items():
            node_info = self.start_entity_node_info_collection.get_first_match_entity_for_qa(entity_fo_qa_list)
            if node_info is None:
                continue
            if self.echo:
                print("find for keyword:", keyword, node_info)
            result.add(node_info)
        return result

    def get_top_node_info_by_each_keywords_three_different_type(self):
        result = set([])
        for (keyword, entity_fo_qa_list) in self.keyword_2_entitynodemap.items():
            node_info_list = self.start_entity_node_info_collection.get_first_match_entity_for_qa_for_three_type_entity(
                entity_fo_qa_list)
            if self.echo:
                print("find for keyword:", keyword, node_info_list)
            for node_info in node_info_list:
                if node_info.qe_sim > MIN_RELATED_ENTITY_SIMILARITY:
                    result.add(node_info)
                    if self.echo:
                        print("keey entity ", keyword, node_info)

        return result

    def get_node_info_collection(self):
        return self.start_entity_node_info_collection

    def get_entity_node_list(self):
        return self.start_entity_node_info_collection.get_entity_list()

    def add_sentence_node_list(self, sentence_node_list):
        for sentence_node in sentence_node_list:
            sentence_info = SentenceInfo(sentence_node, self.defaultSearchAccessor.get_id_for_node(sentence_node))
            self.sentence_info_collection.add(sentence_info)

    def add_api_node_list(self, api_node_list):
        for api_node in api_node_list:
            api_info = APIInfo(api_node, self.defaultSearchAccessor.get_id_for_node(api_node))
            self.api_node_info_collection.add(api_info)

    def print_informat(self):
        for node_info in self.start_entity_node_info_collection.get_all_node_infos():
            print(node_info)

    def get_candidate_sentence_list(self):
        return self.sentence_info_collection.get_all_sentence_infos()

    def get_sentence_size(self):
        return self.sentence_info_collection.size()

    def get_entity_size(self):
        return self.start_entity_node_info_collection.size()

    def print_sentences(self):
        self.sentence_info_collection.print_info()

    def print_entities(self):
        print("print entities for start entity")
        self.start_entity_node_info_collection.print_info()

    def print_api_entities(self):
        print("print api entities for start entity")
        self.api_node_info_collection.print_info()

    def print_top_sentences(self, top=1000):
        for s in self.sentence_info_collection.get_all_sentence_infos()[:top]:
            print(s)

    def get_entity_info_collection(self):
        return self.start_entity_node_info_collection

    def get_sentence_info_collection(self):
        return self.sentence_info_collection

    def fill_api_id_in_result_list(self, result_sentence_list):

        for sentence_dict in result_sentence_list:
            api_entity = self.semanticSearchAccessor.get_api_entity_for_sentence(sentence_dict["kg_id"])
            if api_entity is None:
                continue

            sentence_dict["api_kg_id"] = api_entity["id"]
            sentence_dict["api_id"] = api_entity["api_id"]
            sentence_dict["api_qualified_name"] = api_entity["qualified_name"]
            sentence_dict["api_kg_id"] = self.defaultSearchAccessor.get_id_for_node(api_entity)
            sentence_dict["api_type"] = api_entity["api_type"]
            if "api_document_website#1" in dict(api_entity):
                sentence_dict["api_document_website#1"] = api_entity["api_document_website#1"]

        return result_sentence_list

    def add_api_node_list_from_start_nodes_list(self):
        api_node_list = []
        for node_info in self.start_entity_node_info_collection.node_info_list:
            for entity_for_qa in node_info.entity_for_qa_list:
                if entity_for_qa.source == "api":
                    api_node_list.append(node_info.entity_node)

        self.add_api_node_list(api_node_list)

    def get_api_info_collection(self):
        return self.api_node_info_collection

    def start_build_top_related_entity_info_list(self):
        selected_entity_info_list = self.get_top_node_info_by_each_keywords()
        self.top_related_entity_info_collection = NodeInfoCollection()

        for node_info in selected_entity_info_list:
            self.top_related_entity_info_collection.add(node_info)
        if self.echo:
            print("top_related_entity_info_collection=", self.top_related_entity_info_collection)

    def get_top_related_entity_info_collection(self):
        return self.top_related_entity_info_collection
