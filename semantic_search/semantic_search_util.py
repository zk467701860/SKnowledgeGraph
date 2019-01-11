import traceback

import numpy as np

from db.engine_factory import EngineFactory
from db.search import QAEntitySearcher
from entity_extractor.extractor import EntityExtractor
from semantic_search.matrix_calculation import MatrixCalculation
from semantic_search.model_query_util import KnowledgeGraphFeafureModels, QACacheInfoManager, \
    MIN_RELATED_ENTITY_SIMILARITY
from shared.logger_util import Logger
from skgraph.graph.accessor.graph_accessor import GraphClient, DefaultGraphAccessor
from skgraph.graph.accessor.graph_client_for_sementic_search import SemanticSearchAccessor


class SentenceLevelSemanticSearch:
    SORT_FUNCTION_ENTITIES_BRIDGE = 3
    SORT_FUNCTION_AVERAGE_ENTITY_GRAPH_SIMILAR = 4

    SORT_FUNCTION_AVERAGE_VECTOR = 2

    SORT_FUNCTION_NOT_AVERAGE_GRAPH_VECTOR = 1
    SORT_FUNCTION_SELECT_PART_ENTITY_LINK = 5

    def __init__(self, ):
        self._session = None
        self.kg_models = None
        self._entity_extractor = None

        # self._tf_idf_model = None

        self.qa_searcher = None
        self.semanticSearchAccessor = None
        self.defaultAccessor = None
        self._logger = None

    def init(self, vector_dir_path="./model/"):
        self.kg_models = KnowledgeGraphFeafureModels()
        self.kg_models.init(vector_dir_path=vector_dir_path)

        self._session = EngineFactory.create_session(echo=False)
        self._entity_extractor = EntityExtractor()

        # self._tf_idf_model = TFIDFModel()
        # self._tf_idf_model.load(dict_type=2)

        self.qa_searcher = QAEntitySearcher()
        client = GraphClient(server_number=4)
        self.semanticSearchAccessor = SemanticSearchAccessor(client)
        self.defaultAccessor = DefaultGraphAccessor(client)
        self._logger = Logger("QAResultSearch").get_log()

    def semantic_search(self,
                        query_text,
                        each_np_candidate_entity_num=50,
                        sort_function=SORT_FUNCTION_SELECT_PART_ENTITY_LINK,
                        sentence_limit=20,
                        weight_context_sim=0.6,
                        weight_graph_sim=0.4,

                        ):
        try:
            qa_info_manager = self.get_candidate_sentences(query_text,
                                                           each_np_candidate_entity_num=each_np_candidate_entity_num)

            # sentence_list=qa_info_manager.get_candidate_sentence_list()
            #
            # entity_for_qa_set
            # entity_for_qa_set.print_informat()
            # entity_list = entity_for_qa_set.get_entity_node_list()
            # chunk_to_related_entity_list_map = entity_for_qa_set.keyword_2_entitynodemap

            self._logger.info("entity_list =%d sentence_list=%d" % (
                qa_info_manager.get_entity_size(), qa_info_manager.get_sentence_size()))
            # for n in entity_list:
            #     print("entity", n)
            new_sentence_list = []
            # if sort_function == SentenceLevelSemanticSearch.SORT_FUNCTION_NOT_AVERAGE_GRAPH_VECTOR:
            #     new_sentence_list = self.sort_sentence_by_build_graph_vector_for_query_in_semantic_weight(query_text,
            #                                                                                               sentence_list=sentence_list,
            #                                                                                               entity_list=entity_list,
            #                                                                                               weight_context_sim=weight_context_sim,
            #                                                                                               weight_graph_sim=weight_graph_sim)
            #
            # if sort_function == SentenceLevelSemanticSearch.SORT_FUNCTION_AVERAGE_VECTOR:
            #     new_sentence_list = self.sort_sentence_by_build_average_graph_vector_for_query(query_text,
            #                                                                                    sentence_list=sentence_list,
            #                                                                                    entity_list=entity_list,
            #                                                                                    weight_context_sim=weight_context_sim,
            #                                                                                    weight_graph_sim=weight_graph_sim
            #                                                                                    )
            #
            # if sort_function == SentenceLevelSemanticSearch.SORT_FUNCTION_ENTITIES_BRIDGE:
            #     new_sentence_list = self.sort_sentence_by_entities_as_bridge(query_text,
            #                                                                  sentence_list=sentence_list,
            #                                                                  entity_list=entity_list,
            #                                                                  weight_context_sim=weight_context_sim,
            #                                                                  weight_graph_sim=weight_graph_sim)
            #
            # if sort_function == SentenceLevelSemanticSearch.SORT_FUNCTION_AVERAGE_ENTITY_GRAPH_SIMILAR:
            #     new_sentence_list = self.sort_sentence_by_entities_for_graph_similarity_as_bridge(query_text,
            #                                                                                       sentence_list=sentence_list,
            #                                                                                       entity_list=entity_list,
            #                                                                                       weight_context_sim=weight_context_sim,
            #                                                                                       weight_graph_sim=weight_graph_sim)

            if sort_function == SentenceLevelSemanticSearch.SORT_FUNCTION_SELECT_PART_ENTITY_LINK:
                new_sentence_list = self.sort_sentence_by_select_part_entity_as_bridge(query_text,
                                                                                       qa_info_manager=qa_info_manager,
                                                                                       weight_context_sim=weight_context_sim,
                                                                                       weight_graph_sim=weight_graph_sim,
                                                                                       )


            result_list = qa_info_manager.fill_api_id_in_result_list(new_sentence_list[:sentence_limit])

            self._logger.info("result_list =%d " % len(result_list))

            return result_list
        except Exception:
            self._logger.exception("----qaexception----")
            traceback.print_exc()
            return []

    def get_candidate_sentences(self, query_text, each_np_candidate_entity_num=20):

        chunk_list = self.get_chunk_from_text(query_text)
        print("chunk num=%d %s" % (len(chunk_list), ",".join(chunk_list)))

        qa_info_manager = self.search_entity_by_fulltext(chunk_list, each_np_candidate_entity_num)
        qa_info_manager.start_create_node_info_collection()

        print("related entity for qa", qa_info_manager)

        entity_for_qa_list = qa_info_manager.get_all_entity_for_qa_list()
        print("entity_for_qa_list num=%d" % len(entity_for_qa_list))

        sentence_list = self.search_sentence_by_entity_for_qa_list(entity_for_qa_list)
        print("sentence_list num=%d" % len(sentence_list))
        qa_info_manager.add_sentence_node_list(sentence_list)

        return qa_info_manager

    def expand_the_chunk_by_words(self, final_chunk_list):
        final_set = []
        for chunk in final_chunk_list:
            final_set.append(chunk)
            for word in chunk.split(" "):
                final_set.append(word)
        print("word set", final_set)
        return list(set(final_set))

    def get_chunk_from_text(self, text):

        final_chunk_list = self._entity_extractor.get_all_possible_key_word_from_text(text)

        return final_chunk_list

    def search_entity_by_fulltext(self, chunk_list, each_np_candidate_entity_num=20):
        qa_info_manager = QACacheInfoManager(semanticSearchAccessor=self.semanticSearchAccessor,
                                             defaultSearchAccessor=self.defaultAccessor,
                                             kg_models=self.kg_models)
        for chunk in chunk_list:
            related_entity_list = self.qa_searcher.search_related_entity(chunk, each_np_candidate_entity_num)
            qa_info_manager.add(chunk, related_entity_list)
            related_entity_for_api = self.qa_searcher.search_related_entity_for_api(chunk, each_np_candidate_entity_num)
            qa_info_manager.add(chunk, related_entity_for_api)
        return qa_info_manager

    def search_all_entity_by_fulltext_by_half(self, chunk, each_np_candidate_entity_num=20):
        qa_info_manager = QACacheInfoManager(semanticSearchAccessor=self.semanticSearchAccessor,
                                             defaultSearchAccessor=self.defaultAccessor,
                                             kg_models=self.kg_models)

        related_entity_for_api = self.qa_searcher.search_related_entity_for_api(chunk, each_np_candidate_entity_num/2)
        qa_info_manager.add(chunk, related_entity_for_api)

        related_entity_list = self.qa_searcher.search_related_entity(chunk, each_np_candidate_entity_num/2)
        qa_info_manager.add(chunk, related_entity_list)

        return qa_info_manager

    def search_sentence_by_entity_for_qa_list(self, entity_for_qa_list):
        entity_id_string_list = [str(entity_for_qa.kg_id) for entity_for_qa in entity_for_qa_list]
        entity_id_string_list = list(set(entity_id_string_list))
        return self.semanticSearchAccessor.search_sentence_by_entity_list(entity_id_string_list=entity_id_string_list)

    def get_relation_by_nodes(self, node_list):
        return self.semanticSearchAccessor.get_nodes_relation(node_list)

    def sort_sentence_by_entities_as_bridge(self, question,
                                            sentence_list,
                                            entity_list,
                                            weight_context_sim=0.5,
                                            weight_graph_sim=0.5
                                            ):
        self._logger.info("run sort_sentence_by_entities_as_bridge get result=%d" % len(sentence_list))

        question_vec = self.kg_models.get_question_entity_vector(question)

        entity_vec_list, entity_graph_vec_list = self.kg_models.get_vectors_for_entity_list(entity_list)
        sentence_vec_list, sentence_graph_vec_list = self.kg_models.get_vectors_for_entity_list(sentence_list)

        qe_sim_np = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_vec, entity_vec_list)
        qe_sim_np = qe_sim_np / qe_sim_np.sum()

        kg_context_sim = MatrixCalculation.compute_cossin_for_matrix_to_matrix_normalize(entity_vec_list,
                                                                                         sentence_vec_list)
        kg_graph_sim = MatrixCalculation.compute_cossin_for_matrix_to_matrix_normalize(entity_graph_vec_list,
                                                                                       sentence_graph_vec_list)

        qs_context_sim = weight_context_sim * qe_sim_np * kg_context_sim
        qs_graph_sim = weight_graph_sim * qe_sim_np * kg_graph_sim

        qs_sim = qs_context_sim + qs_graph_sim
        qs_sim = qs_sim.tolist()[0]
        qs_context_sim = qs_context_sim.tolist()[0]
        qs_graph_sim = qs_graph_sim.tolist()[0]

        for sum_sim, sentence, context_sim, graph_sim in zip(qs_sim, sentence_list, qs_context_sim, qs_graph_sim):
            sentence["qs_sim"] = sum_sim
            sentence["qs_context_sim"] = context_sim
            sentence["qs_graph_sim"] = graph_sim

        result = []
        for sentence in sentence_list:
            result.append({
                "kg_id": self.defaultAccessor.get_id_for_node(sentence),
                "sentence_id": sentence["sentence_id"],
                "sentence_type": sentence["sentence_type_code"],
                "text": sentence["sentence_text"],
                "qs_sim": sentence["qs_sim"],
                "qs_context_sim": sentence["qs_context_sim"],
                "qs_graph_sim": sentence["qs_graph_sim"]

            })
        self._logger.info("run sort_sentence_by_entities_as_bridge get result num=%d" % len(result))
        result.sort(key=lambda k: (k.get('qs_sim', 0)), reverse=True)

        return result

    def sort_sentence_by_entities_for_graph_similarity_as_bridge(self, question,
                                                                 sentence_list,
                                                                 entity_list,
                                                                 weight_context_sim=0.5,
                                                                 weight_graph_sim=0.5
                                                                 ):
        self._logger.info(
            "run sort_sentence_by_entities_for_graph_similarity_as_bridge get result=%d" % len(sentence_list))

        question_context_vec = self.kg_models.get_question_entity_vector(question)

        entity_vec_list, entity_graph_vec_list = self.kg_models.get_vectors_for_entity_list(entity_list)
        sentence_vec_list, sentence_graph_vec_list = self.kg_models.get_vectors_for_entity_list(sentence_list)

        qe_sim_np = np.ones((1, len(entity_list)))
        qe_sim_np = qe_sim_np / qe_sim_np.sum()
        qs_context_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                      sentence_vec_list)

        kg_graph_sim = MatrixCalculation.compute_cossin_for_matrix_to_matrix_normalize(entity_graph_vec_list,
                                                                                       sentence_graph_vec_list)

        qs_context_sim = weight_context_sim * qs_context_sim
        qs_graph_sim = weight_graph_sim * qe_sim_np * kg_graph_sim

        qs_sim = qs_context_sim + qs_graph_sim
        qs_sim = qs_sim.tolist()[0]
        qs_context_sim = qs_context_sim.tolist()[0]
        qs_graph_sim = qs_graph_sim.tolist()[0]

        for sum_sim, sentence, context_sim, graph_sim in zip(qs_sim, sentence_list, qs_context_sim, qs_graph_sim):
            sentence["qs_sim"] = sum_sim
            sentence["qs_context_sim"] = context_sim
            sentence["qs_graph_sim"] = graph_sim

        result = []
        for sentence in sentence_list:
            result.append({
                "kg_id": self.defaultAccessor.get_id_for_node(sentence),
                "sentence_id": sentence["sentence_id"],
                "sentence_type": sentence["sentence_type_code"],
                "text": sentence["sentence_text"],
                "qs_sim": sentence["qs_sim"],
                "qs_context_sim": sentence["qs_context_sim"],
                "qs_graph_sim": sentence["qs_graph_sim"]

            })
        self._logger.info("run sort_sentence_by_entities_as_bridge get result num=%d" % len(result))
        result.sort(key=lambda k: (k.get('qs_sim', 0)), reverse=True)

        print("sorted result")
        for t in result:
            print("test sort", t)
        print(result[:100])

        return result

    def sort_sentence_by_build_average_graph_vector_for_query(self, question, sentence_list, entity_list,
                                                              weight_context_sim=0.5, weight_graph_sim=0.5
                                                              ):
        self._logger.info(
            "run sort_sentence_by_build_average_graph_vector_for_query get sentence_list=%d" % len(sentence_list))

        kg_models = self.kg_models
        question_context_vec = kg_models.get_question_entity_vector(question)
        entity_vec_list, entity_graph_vec_list = self.kg_models.get_vectors_for_entity_list(entity_list)
        sentence_vec_list, sentence_graph_vec_list = self.kg_models.get_vectors_for_entity_list(sentence_list)

        entity_list, entity_vec_list, entity_graph_vec_list = self.remove_the_not_related_entity(entity_graph_vec_list,
                                                                                                 entity_list,
                                                                                                 entity_vec_list,
                                                                                                 question_context_vec)

        query_graph_vector = kg_models.get_question_graph_vector_by_average_all_entities(
            question=question,
            entity_graph_vec_list=entity_graph_vec_list)

        qs_context_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                      sentence_vec_list)

        qs_graph_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(query_graph_vector,
                                                                                    sentence_graph_vec_list)
        qs_context_sim = weight_context_sim * qs_context_sim

        qs_graph_sim = weight_graph_sim * qs_graph_sim

        qs_sim = qs_context_sim + qs_graph_sim

        qs_sim = qs_sim.tolist()[0]
        qs_context_sim = qs_context_sim.tolist()[0]
        qs_graph_sim = qs_graph_sim.tolist()[0]

        for sum_sim, sentence, context_sim, graph_sim in zip(qs_sim, sentence_list, qs_context_sim, qs_graph_sim):
            sentence["qs_sim"] = sum_sim
            sentence["qs_context_sim"] = context_sim
            sentence["qs_graph_sim"] = graph_sim

        result = []
        for sentence in sentence_list:
            result.append({
                "kg_id": self.defaultAccessor.get_id_for_node(sentence),
                "sentence_id": sentence["sentence_id"],
                "text": sentence["sentence_text"],
                "sentence_type": sentence["sentence_type_code"],
                "qs_sim": sentence["qs_sim"],
                "qs_context_sim": sentence["qs_context_sim"],
                "qs_graph_sim": sentence["qs_graph_sim"]

            })
        self._logger.info("run sort_sentence_by_build_average_graph_vector_for_query get result num=%d" % len(result))
        result.sort(key=lambda k: (k.get('qs_sim', 0)), reverse=True)

        return result

    def sort_sentence_by_select_part_entity_as_bridge(self, question,
                                                      qa_info_manager,
                                                      # sentence_list,
                                                      # entity_list,
                                                      weight_context_sim=0.6,
                                                      weight_graph_sim=0.4,
                                                      # chunk_to_related_entity_list_map=None,
                                                      ):
        self._logger.info(
            "run sort part entity result=%d" % qa_info_manager.get_sentence_size())

        print("entity for node")
        qa_info_manager.print_entities()
        print("sentence for node")
        # qa_info_manager.print_sentences()

        entity_info_collection = qa_info_manager.get_entity_info_collection()
        sentence_info_collection = qa_info_manager.get_sentence_info_collection()
        entity_info_collection.init_vectors(self.kg_models)
        sentence_info_collection.init_vectors(self.kg_models)
        sentence_list = sentence_info_collection.get_entity_list()
        entity_vec_list = entity_info_collection.get_entity_context_list()
        entity_graph_vec_list = entity_info_collection.get_entity_graph_list()
        entity_list = entity_info_collection.get_entity_list()
        sentence_vec_list = sentence_info_collection.get_entity_context_list()
        sentence_graph_vec_list = sentence_info_collection.get_entity_graph_list()

        question_context_vec = self.kg_models.get_question_entity_vector(question)

        entity_list, entity_vec_list, entity_graph_vec_list = self.get_top_related_entity_info_list(
            question_context_vec=question_context_vec, qa_info_manager=qa_info_manager)

        # entity_list, entity_vec_list, entity_graph_vec_list = self.remove_the_not_related_entity_by_only_save_one_for_each(
        #     entity_graph_vec_list=entity_graph_vec_list, entity_vec_list=entity_vec_list, entity_list=entity_list,
        #     question_context_vec=question_context_vec,
        #     qa_info_manager=qa_info_manager
        #
        # )

        qs_context_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                      sentence_vec_list)
        # todo:change to the average graph similarity
        # qs_graph_sim = self.get_graph_similarity_by_average_entity_graph_vector(entity_graph_vec_list, question,
        #                                                                         sentence_graph_vec_list)

        qs_graph_sim = self.get_query_to_sentence_graph_sim_by_select_top_enttity(entity_graph_vec_list, entity_list,
                                                                                  entity_vec_list,
                                                                                  sentence_graph_vec_list,
                                                                                  sentence_vec_list)

        qs_context_sim = weight_context_sim * qs_context_sim
        qs_graph_sim = weight_graph_sim * qs_graph_sim

        qs_sim = qs_context_sim + qs_graph_sim
        qs_sim = qs_sim.tolist()[0]
        qs_context_sim = qs_context_sim.tolist()[0]
        qs_graph_sim = qs_graph_sim.tolist()[0]

        for sum_sim, sentence, context_sim, graph_sim in zip(qs_sim, sentence_list, qs_context_sim, qs_graph_sim):
            sentence["qs_sim"] = sum_sim
            sentence["qs_context_sim"] = context_sim
            sentence["qs_graph_sim"] = graph_sim

        result = []
        for sentence in sentence_list:
            result.append({
                "kg_id": self.defaultAccessor.get_id_for_node(sentence),
                "sentence_id": sentence["sentence_id"],
                "sentence_type": sentence["sentence_type_code"],
                "text": sentence["sentence_text"],
                "qs_sim": sentence["qs_sim"],
                "qs_context_sim": sentence["qs_context_sim"],
                "qs_graph_sim": sentence["qs_graph_sim"]

            })
        self._logger.info("run sort_sentence_by_entities_as_bridge get result num=%d" % len(result))
        result.sort(key=lambda k: (k.get('qs_sim', 0)), reverse=True)

        print(result[:100])

        return result

    def get_graph_similarity_by_average_entity_graph_vector(self, entity_graph_vec_list, question,
                                                            sentence_graph_vec_list):
        query_graph_vector = self.kg_models.get_question_graph_vector_by_average_all_entities(
            question=question,
            entity_graph_vec_list=entity_graph_vec_list)
        qs_graph_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(query_graph_vector,
                                                                                    sentence_graph_vec_list)
        return qs_graph_sim

    def get_graph_similarity_average_entity_graph_vector_similarity(self, entity_graph_vec_list, question,
                                                                    sentence_graph_vec_list):
        # query_graph_vector = self.kg_models.get_question_graph_vector_by_average_all_entities(
        #     question=question,
        #     entity_graph_vec_list=entity_graph_vec_list)
        qs_graph_sim = MatrixCalculation.compute_cossin_for_matrix_to_matrix_normalize(sentence_graph_vec_list,
                                                                                       entity_graph_vec_list)
        return np.mean(qs_graph_sim, axis=1)

    def get_query_to_sentence_graph_sim_by_select_top_enttity(self, entity_graph_vec_list, entity_list, entity_vec_list,
                                                              sentence_graph_vec_list, sentence_vec_list):
        # kg_se_graph_sim = MatrixCalculation.compute_cossin_for_matrix_to_matrix_normalize(sentence_graph_vec_list,
        #                                                                                   entity_graph_vec_list,
        #                                                                                   )
        kg_se_context_sim = MatrixCalculation.compute_cossin_for_matrix_to_matrix_normalize(
            sentence_vec_list,
            entity_vec_list)
        # TODO
        # kg_se_sim = 0.5 * kg_se_graph_sim + 0.5 * kg_se_context_sim
        kg_se_sim = kg_se_context_sim

        print("final entity list", len(entity_list), entity_list)
        select_linking_entity_num = min(5, len(entity_list))
        onehot_maxsim_se_matrix = MatrixCalculation.get_most_similar_top_n_entity_as_matrix(
            top_n=select_linking_entity_num, s_e_similarity_matrix=kg_se_sim)
        s_query_graph_vec_matrix = onehot_maxsim_se_matrix * np.matrix(
            entity_graph_vec_list) / select_linking_entity_num
        qs_graph_sim = MatrixCalculation.compute_cossin_for_one_to_one_in_two_list_normalize(sentence_graph_vec_list,
                                                                                             s_query_graph_vec_matrix.getA())
        return qs_graph_sim

    def remove_the_not_related_entity_by_only_save_one_for_each(self, entity_graph_vec_list, entity_list,
                                                                entity_vec_list, question_context_vec,
                                                                qa_info_manager):
        chunk_to_related_entity_list_map = qa_info_manager.keyword_2_entitynodemap
        qe_sim_np = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                 entity_vec_list)

        entity_info_sumary_list = []
        for (entity, sim, entity_vec, entity_graph_vec) in zip(entity_list, qe_sim_np.getA()[0], entity_vec_list,
                                                               entity_graph_vec_list):
            print("after first removing sim=", sim, "entity=", entity)
            entity_info_sumary_list.append({"entity": entity,
                                            "sim": sim,
                                            "entity_vec": entity_vec,
                                            "entity_graph_vec": entity_graph_vec
                                            })

        entity_info_sumary_list.sort(key=lambda k: (k.get('sim', 0)), reverse=True)

        valid_word_set = set([])
        word_to_related_entity_list_map = {}

        for chunk, related_entity_list in chunk_to_related_entity_list_map.items():
            word = chunk
            if word not in valid_word_set:
                valid_word_set.add(word)
                word_to_related_entity_list_map[word] = related_entity_list
            else:
                word_to_related_entity_list_map[word].extend(related_entity_list)

        # clean_entity_info_list = self.get_clean_entity_for_each_word_by_max_similarity(entity_info_sumary_list,
        #                                                                                word_to_related_entity_list_map)
        #
        clean_entity_info_list = self.get_clean_entity_for_each_word_by_max_n_similarity(entity_info_sumary_list,
                                                                                         word_to_related_entity_list_map)

        new_entity_list = []
        new_entity_graph_vec_list = []
        new_entity_vec_list = []
        for entity_info_sumary in clean_entity_info_list:
            new_entity_list.append(entity_info_sumary["entity"])
            new_entity_graph_vec_list.append(entity_info_sumary["entity_graph_vec"])
            new_entity_vec_list.append(entity_info_sumary["entity_vec"])
            print("final save sim=", entity_info_sumary["sim"], "entity=", entity_info_sumary["entity"])

        return new_entity_list, new_entity_vec_list, new_entity_graph_vec_list

    def get_top_related_entity_info_list(self, question_context_vec,
                                         qa_info_manager):

        node_info_collection = qa_info_manager.get_node_info_collection()
        node_info_collection.fill_each_entity_with_similary_to_question(question_context_vec)
        node_info_collection.sort_by_qe_sim()

        # selected_entity_info_list = qa_info_manager.get_top_node_info_by_each_keywords_three_different_type()
        selected_entity_info_list = qa_info_manager.get_top_node_info_by_each_keywords()

        new_entity_list = []
        new_entity_vec_list = []
        new_entity_graph_vec_list = []
        for node_info in selected_entity_info_list:
            new_entity_list.append(node_info.entity_node)
            new_entity_vec_list.append(node_info.entity_context_vec)
            new_entity_graph_vec_list.append(node_info.entity_graph_vec)

        return new_entity_list, new_entity_vec_list, new_entity_graph_vec_list

    def get_clean_entity_for_each_word_by_max_n_similarity(self, entity_info_sumary_list,
                                                           word_to_related_entity_list_map):
        clean_entity_kg_id_list = set([])
        print("start get_clean_entity_infi_sumary_list ")
        word_name_entity_mark = {}
        for valid_word, related_entity_list in word_to_related_entity_list_map.items():
            print("valid word=", valid_word)

            entity_info_list = self.get_first_from_entity_info_sumary_list_and_in_related_entity_list(
                entity_info_sumary_list, related_entity_list, 3)

            # for entity_info in entity_info_list:
            print("get candidate for word=", valid_word, entity_info_list)
            word_name_entity_mark[valid_word] = entity_info_list

            clean_entity_info_list = []
            clean_entity_kg_id_list = set([])

            for word, entity_info_list in word_name_entity_mark.items():
                for entity_info in entity_info_list:
                    kg_id = self.defaultAccessor.get_id_for_node(entity_info["entity"])
                    if kg_id not in clean_entity_kg_id_list:
                        clean_entity_info_list.append(entity_info)
                        clean_entity_kg_id_list.add(kg_id)
                        print("valid word=", word, entity_info["entity"])
        return clean_entity_info_list

    def get_clean_entity_for_each_word_by_max_similarity(self, entity_info_sumary_list,
                                                         word_to_related_entity_list_map):
        clean_entity_kg_id_list = set([])
        print("start get_clean_entity_infi_sumary_list ")
        word_name_entity_mark = {}
        for valid_word, related_entity_list in word_to_related_entity_list_map.items():
            print("valid word=", valid_word)

            entity_info_list = self.get_first_from_entity_info_sumary_list_and_in_related_entity_list(
                entity_info_sumary_list, related_entity_list)

            for entity_info in entity_info_list:
                print("get candidate for word=", valid_word, entity_info["entity"])
                word_name_entity_mark[valid_word] = entity_info

            clean_entity_info_list = []
            clean_entity_kg_id_list = set([])

            for word, entity_info in word_name_entity_mark.items():
                kg_id = self.defaultAccessor.get_id_for_node(entity_info["entity"])
                if kg_id not in clean_entity_kg_id_list:
                    clean_entity_info_list.append(entity_info)
                    clean_entity_kg_id_list.add(kg_id)
                    print("valid word=", word, entity_info["entity"])
        return clean_entity_info_list

    def get_clean_entity_infi_sumary_list(self, entity_info_sumary_list, word_to_related_entity_list_map):
        clean_entity_kg_id_list = set([])
        print("start get_clean_entity_infi_sumary_list ")
        word_name_entity_mark = {}
        for valid_word, related_entity_list in word_to_related_entity_list_map.items():
            print("valid word=", valid_word)

            entity_info_list = self.get_first_from_entity_info_sumary_list_and_in_related_entity_list(
                entity_info_sumary_list, related_entity_list)

            for entity_info in entity_info_list:
                kg_id = self.defaultAccessor.get_id_for_node(entity_info["entity"])
                print("get candidate for word=", valid_word, entity_info["entity"])

                if kg_id not in clean_entity_kg_id_list:
                    if valid_word not in word_name_entity_mark.keys():
                        word_name_entity_mark[valid_word] = entity_info
                    else:
                        old_entity_info = word_name_entity_mark[valid_word]
                        if entity_info["sim"] > old_entity_info["sim"]:
                            word_name_entity_mark[valid_word] = entity_info

                    for seperate_name in valid_word.split(" "):
                        if seperate_name not in word_name_entity_mark.keys():
                            word_name_entity_mark[seperate_name] = entity_info
                        else:
                            old_entity_info = word_name_entity_mark[seperate_name]
                            if entity_info["sim"] > old_entity_info["sim"]:
                                word_name_entity_mark[seperate_name] = entity_info

                clean_entity_kg_id_list.add(kg_id)

            clean_entity_info_list = []
            clean_entity_kg_id_list = set([])

            for word, entity_info in word_name_entity_mark.items():
                kg_id = self.defaultAccessor.get_id_for_node(entity_info["entity"])
                if kg_id not in clean_entity_kg_id_list:
                    clean_entity_info_list.append(entity_info)
                    clean_entity_kg_id_list.add(kg_id)
                    print("valid word=", word, entity_info["entity"])
        return clean_entity_info_list

    def remove_the_not_related_entity(self, entity_graph_vec_list, entity_list, entity_vec_list, question_context_vec):

        qe_sim_np = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                 entity_vec_list)
        print("qeustion to entity similary")

        new_entity_list = []
        new_entity_vec_list = []
        new_entity_graph_vec_list = []
        qe_sim_clean = []
        for (entity, sim, entity_vec, entity_graph_vec) in zip(entity_list, qe_sim_np.getA()[0], entity_vec_list,
                                                               entity_graph_vec_list):
            print("sim=", sim, "entity=", entity)
            if sim > MIN_RELATED_ENTITY_SIMILARITY:
                print("adding ", entity)
                new_entity_list.append(entity)
                new_entity_vec_list.append(entity_vec)
                new_entity_graph_vec_list.append(entity_graph_vec)
                qe_sim_clean.append(sim)

        entity_list = new_entity_list
        entity_vec_list = new_entity_vec_list
        entity_graph_vec_list = new_entity_graph_vec_list

        new_entity_list = []
        new_entity_vec_list = []
        new_entity_graph_vec_list = []

        entity_info_sumary_list = []

        for (entity, sim, entity_vec, entity_graph_vec) in zip(entity_list, qe_sim_clean, entity_vec_list,
                                                               entity_graph_vec_list):
            print("after first removing sim=", sim, "entity=", entity)
            entity_info_sumary_list.append({"entity": entity,
                                            "sim": sim,
                                            "entity_vec": entity_vec,
                                            "entity_graph_vec": entity_graph_vec
                                            })

        entity_info_sumary_list.sort(key=lambda k: (k.get('sim', 0)), reverse=True)

        api_class_name_set = set([])

        new_entity_info_sumary_list = []
        for entity_info_sumary in entity_info_sumary_list:
            if entity_info_sumary["entity"].has_label("api"):
                qualified_name = entity_info_sumary["entity"]["qualified_name"]
                if qualified_name in api_class_name_set:
                    continue
                if "(" in qualified_name:
                    simple_name = qualified_name.split("(")[0]

                    class_name = ".".join(simple_name.split(".")[:-1])
                    if class_name in api_class_name_set:
                        continue
                    else:
                        api_class_name_set.add(class_name)
                        new_entity_info_sumary_list.append(entity_info_sumary)
                else:
                    api_class_name_set.add(qualified_name)
                    new_entity_info_sumary_list.append(entity_info_sumary)
            else:
                new_entity_info_sumary_list.append(entity_info_sumary)

        for entity_info_sumary in new_entity_info_sumary_list:
            new_entity_list.append(entity_info_sumary["entity"])
            new_entity_graph_vec_list.append(entity_info_sumary["entity_graph_vec"])
            new_entity_vec_list.append(entity_info_sumary["entity_vec"])
            print("final save sim=", entity_info_sumary["sim"], "entity=", entity_info_sumary["entity"])

        return new_entity_list, new_entity_vec_list, new_entity_graph_vec_list

    def sort_sentence_by_build_graph_vector_for_query_in_semantic_weight(self, question, sentence_list, entity_list,
                                                                         weight_context_sim=0.5, weight_graph_sim=0.5
                                                                         ):

        self._logger.info(
            "run sort_sentence_by_build_graph_vector_for_query_in_semantic_weight get sentence_list=%d" % len(
                sentence_list))

        kg_models = self.kg_models
        question_context_vec = kg_models.get_question_entity_vector(question)
        entity_vec_list, entity_graph_vec_list = self.kg_models.get_vectors_for_entity_list(entity_list)
        sentence_vec_list, sentence_graph_vec_list = self.kg_models.get_vectors_for_entity_list(sentence_list)

        query_graph_vector = kg_models.get_question_graph_vector_by_semantic_weight_all_entities(
            question_context_vec=question_context_vec,
            entity_context_vec_list=entity_vec_list,
            entity_graph_vec_list=entity_graph_vec_list)

        qs_context_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                      sentence_vec_list)

        qs_graph_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(query_graph_vector,
                                                                                    sentence_graph_vec_list)
        qs_context_sim = weight_context_sim * qs_context_sim

        qs_graph_sim = weight_graph_sim * qs_graph_sim

        qs_sim = qs_context_sim + qs_graph_sim

        qs_sim = qs_sim.tolist()[0]
        qs_context_sim = qs_context_sim.tolist()[0]
        qs_graph_sim = qs_graph_sim.tolist()[0]

        for sum_sim, sentence, context_sim, graph_sim in zip(qs_sim, sentence_list, qs_context_sim, qs_graph_sim):
            sentence["qs_sim"] = sum_sim
            sentence["qs_context_sim"] = context_sim
            sentence["qs_graph_sim"] = graph_sim

        result = []
        for sentence in sentence_list:
            result.append({
                "kg_id": self.defaultAccessor.get_id_for_node(sentence),
                "sentence_id": sentence["sentence_id"],
                "text": sentence["sentence_text"],
                "qs_sim": sentence["qs_sim"],
                "qs_context_sim": sentence["qs_context_sim"],
                "qs_graph_sim": sentence["qs_graph_sim"]
            })
        self._logger.info(
            "run sort_sentence_by_build_graph_vector_for_query_in_semantic_weight get result=%d" % len(result))
        result.sort(key=lambda k: (k.get('qs_sim', 0)), reverse=True)

        return result

    def get_all_entity(self, entity_for_qa_list):
        entity_id_string_list = [str(entity_for_qa.kg_id) for entity_for_qa in entity_for_qa_list]
        entity_id_string_list = list(set(entity_id_string_list))
        return self.semanticSearchAccessor.get_all_entity(entity_id_string_list=entity_id_string_list)

    def get_first_from_entity_info_sumary_list_and_in_related_entity_list(self, entity_info_sumary_list,
                                                                          related_entity_list, top_relate_entity_num=1):
        return_result_list = []
        for entity_info in entity_info_sumary_list:
            kg_id = self.defaultAccessor.get_id_for_node(entity_info["entity"])
            entity = self.get_entity_from_entity_list_by_kgid(kg_id, related_entity_list)
            if entity is not None:
                return_result_list.append(entity_info)
                if len(return_result_list) >= top_relate_entity_num:
                    return return_result_list
        return []

    def get_entity_from_entity_list_by_kgid(self, kg_id, related_entity_list):
        for related_entity in related_entity_list:
            if related_entity.kg_id == kg_id:
                return related_entity
        return None
