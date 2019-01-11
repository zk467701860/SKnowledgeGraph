import traceback

import numpy as np

from db.engine_factory import EngineFactory
from db.search import QAEntitySearcher
from entity_extractor.extractor import EntityExtractor
from semantic_search.matrix_calculation import MatrixCalculation
from semantic_search.model_query_util import KnowledgeGraphFeafureModels, QACacheInfoManager, SentenceInfoCollection
from shared.logger_util import Logger
from skgraph.graph.accessor.graph_accessor import GraphClient, DefaultGraphAccessor
from skgraph.graph.accessor.graph_client_for_sementic_search import SemanticSearchAccessor


class APISentenceLevelSemanticSearch:
    def __init__(self, echo=False):
        self._session = None
        self.kg_models = None
        self._entity_extractor = None
        self.echo = echo
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
                        sentence_limit=20,
                        weight_context_sim=0.6,
                        weight_graph_sim=0.4,
                        ):
        try:
            qa_info_manager = self.get_candidate_api_entity_list(query_text,
                                                                 each_np_candidate_entity_num=each_np_candidate_entity_num)
            qa_info_manager = self.sort_api_by_select_part_entity_as_bridge(query_text,
                                                                            qa_info_manager=qa_info_manager,
                                                                            weight_context_sim=weight_context_sim,
                                                                            weight_graph_sim=weight_graph_sim,
                                                                            )

            valid_api_info_list = qa_info_manager.get_api_info_collection().api_info_list[:100]
            # for index, api_info in enumerate(valid_api_info_list):
            #     print(index, api_info)
            sentence_list = self.get_candidate_sentence_by_api_info_list(valid_api_info_list)
            qa_info_manager.add_sentence_node_list(sentence_list)

            self.sort_sentence_by_select_part_entity_as_bridge(query_text,
                                                               qa_info_manager=qa_info_manager,
                                                               weight_context_sim=weight_context_sim,
                                                               weight_graph_sim=weight_graph_sim,
                                                               )

            valid_sentence_info_list = qa_info_manager.get_sentence_info_collection().sentence_info_list[
                                       :sentence_limit]
            for index, sentence_info in enumerate(valid_sentence_info_list):
                self.fill_api_id_in_result_list_for_one_sentence_info(sentence_info)
                # print(index, sentence_info)
            result = qa_info_manager.get_sentence_info_collection().get_top_n_json(top_n=sentence_limit)
            # print ("%%%%%%%%%%%%%%%%%%%%%%%5")
            # print result
            return result
        except Exception:
            self._logger.exception("----qaexception----")
            traceback.print_exc()
            return []

    def semantic_search_summary_by_api_with_class(self,
                                                  query_text,
                                                  each_np_candidate_entity_num=50,
                                                  sentence_limit=100,
                                                  weight_context_sim=0.6,
                                                  weight_graph_sim=0.4,
                                                  top_api_class_num=10,
                                                  each_api_class_sentence_number=5,
                                                  ):
        try:
            qa_info_manager = self.get_candidate_api_entity_list(query_text,
                                                                 each_np_candidate_entity_num=each_np_candidate_entity_num)
            qa_info_manager = self.sort_api_by_select_part_entity_as_bridge(query_text,
                                                                            qa_info_manager=qa_info_manager,
                                                                            weight_context_sim=weight_context_sim,
                                                                            weight_graph_sim=weight_graph_sim,
                                                                            )

            top_api_class_group = qa_info_manager.get_api_info_collection().get_top_api_info_group_by_api_class()
            result_info_collection_list = []
            for k, v_list in top_api_class_group.items():
                try:
                    # for v in v_list:
                    #     print(k, v)
                    sentence_list = self.get_candidate_sentence_by_api_info_list(v_list)

                    sentence_info_collection = SentenceInfoCollection()
                    for sentence in sentence_list:
                        sentence_info_collection.add_sentence_node(sentence,
                                                                   self.defaultAccessor.get_id_for_node(sentence))
                    sentence_info_collection.filter_others_sentences()

                    sentence_info_collection = self.sort_sentences_for_one_api_class(question=query_text,
                                                                                     qa_info_manager=qa_info_manager,
                                                                                     weight_context_sim=weight_context_sim,
                                                                                     weight_graph_sim=weight_graph_sim,
                                                                                     sentence_info_collection=sentence_info_collection
                                                                                     )
                    sub_collection = sentence_info_collection.get_top_n_as_sub_sentence_collection(
                        top_n=each_api_class_sentence_number)

                    result_info_collection_list.append(sub_collection)
                except:
                    ##How do I convert a String to an int in Java will has problem
                    ## How do I create a file and write to it in Java?
                    traceback.print_exc()

            result_info_collection_list.sort(key=lambda k: (k.get_sum_qs_sim()), reverse=True)

            # final_sentence_info_collection = SentenceInfoCollection()
            #
            # for collection in result_info_collection_list[:top_api_class]:
            #     for sentence_info in collection.get_all_sentence_infos():
            #         self.fill_api_id_in_result_list_for_one_sentence_info(sentence_info)
            #         final_sentence_info_collection.add(sentence_info)
            #
            # sentence_json_list = final_sentence_info_collection.get_all_as_json()
            #
            # return sentence_json_list
            top_related_api_sentence_info_collection_list = result_info_collection_list[:top_api_class_num]
            for sentence_in_collection in result_info_collection_list:
                for sentence_info in sentence_in_collection.get_all_sentence_infos():
                    self.fill_api_id_in_result_list_for_one_sentence_info(sentence_info)

            return top_related_api_sentence_info_collection_list
        except Exception:
            self._logger.exception("----qaexception----")
            traceback.print_exc()
            return []

    def get_candidate_sentence_by_api_info_list(self, api_info_list):
        id_list = [str(api_info.node_id) for api_info in api_info_list]
        return self.semanticSearchAccessor.search_sentence_by_directly_to_api(id_list)

    def get_candidate_api_entity_list(self, query_text, each_np_candidate_entity_num=20):

        chunk_list = self.get_chunk_from_text(query_text)
        print("chunk num=%d %s" % (len(chunk_list), ",".join(chunk_list)))

        qa_info_manager = self.search_entity_by_fulltext(chunk_list, each_np_candidate_entity_num)
        qa_info_manager.start_create_node_info_collection()

        # print("related entity for qa", qa_info_manager)

        entity_info_collection = qa_info_manager.get_entity_info_collection()
        entity_info_collection.init_vectors(self.kg_models)

        question_context_vec = self.kg_models.get_question_entity_vector(query_text)

        self.filter_the_middle_entity_by_small_similarity_to_question_entity(
            question_context_vec=question_context_vec, qa_info_manager=qa_info_manager)

        node_kg_id_str_list = entity_info_collection.get_node_kg_id_str_list()

        api_entity_list = self.search_api_by_node_kg_id_list(node_kg_id_str_list)

        # print("api_entity_list num=%d" % len(api_entity_list))
        qa_info_manager.add_api_node_list(api_entity_list)
        qa_info_manager.add_api_node_list_from_start_nodes_list()
        qa_info_manager.api_node_info_collection.init_vectors(self.kg_models)

        self.filter_api_entity_the_small_similarity_to_question_entity(
            question_context_vec=question_context_vec, qa_info_manager=qa_info_manager)

        # qa_info_manager.print_entities()
        # qa_info_manager.print_api_entities()
        print("api info collection after filter size=%r" % qa_info_manager.api_node_info_collection.size())

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
        final_chunk_list = set(final_chunk_list)

        if len(final_chunk_list) <= 1:
            final_chunk_list.add(text)

        return list(final_chunk_list)

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

        related_entity_for_api = self.qa_searcher.search_related_entity_for_api(chunk, each_np_candidate_entity_num / 2)
        qa_info_manager.add(chunk, related_entity_for_api)

        related_entity_list = self.qa_searcher.search_related_entity(chunk, each_np_candidate_entity_num / 2)
        qa_info_manager.add(chunk, related_entity_list)

        return qa_info_manager

    def search_sentence_by_entity_for_qa_list(self, entity_for_qa_list):
        entity_id_string_list = [str(entity_for_qa.kg_id) for entity_for_qa in entity_for_qa_list]
        entity_id_string_list = list(set(entity_id_string_list))
        return self.semanticSearchAccessor.search_sentence_by_entity_list(entity_id_string_list=entity_id_string_list)

    def search_api_by_entity_for_qa_list(self, entity_for_qa_list):
        entity_id_string_list = [str(entity_for_qa.kg_id) for entity_for_qa in entity_for_qa_list]
        entity_id_string_list = list(set(entity_id_string_list))
        return self.semanticSearchAccessor.search_api_by_entity_list(entity_id_string_list=entity_id_string_list)

    def search_api_by_node_kg_id_list(self, entity_id_string_list):
        return self.semanticSearchAccessor.search_api_by_entity_list(entity_id_string_list=entity_id_string_list)

    def get_relation_by_nodes(self, node_list):
        return self.semanticSearchAccessor.get_nodes_relation(node_list)

    def sort_api_by_select_part_entity_as_bridge(self, question,
                                                 qa_info_manager,
                                                 weight_context_sim=0.6,
                                                 weight_graph_sim=0.4,
                                                 ):

        api_info_collection = qa_info_manager.get_api_info_collection()

        api_entity_list = api_info_collection.get_entity_list()
        api_context_vec_list = api_info_collection.get_entity_context_list()
        api_graph_vec_list = api_info_collection.get_entity_graph_list()
        question_context_vec = self.kg_models.get_question_entity_vector(question)

        entity_info_collection = qa_info_manager.get_top_related_entity_info_collection()
        entity_list = entity_info_collection.get_entity_list()
        entity_context_vec_list = entity_info_collection.get_entity_context_list()
        entity_graph_vec_list = entity_info_collection.get_entity_graph_list()

        qe_context_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                      api_context_vec_list)

        # todo:change to the average graph similarity
        qe_graph_sim = self.get_graph_similarity_by_average_entity_graph_vector(entity_graph_vec_list, question,
                                                                                api_graph_vec_list)

        # qe_graph_sim = self.get_query_to_sentence_graph_sim_by_select_top_enttity(entity_graph_vec_list, entity_list,
        #                                                                           entity_context_vec_list,
        #                                                                           api_graph_vec_list,
        #                                                                           api_context_vec_list)
        #
        qe_context_sim = weight_context_sim * qe_context_sim
        qe_graph_sim = weight_graph_sim * qe_graph_sim

        qe_sim = qe_context_sim + qe_graph_sim
        qe_sim = qe_sim.tolist()[0]
        qe_context_sim = qe_context_sim.tolist()[0]
        qe_graph_sim = qe_graph_sim.tolist()[0]

        for api_info, sum_sim, sentence, context_sim, graph_sim in zip(
                qa_info_manager.get_api_info_collection().api_info_list, qe_sim, api_entity_list, qe_context_sim,
                qe_graph_sim):
            api_info.qe_sim = sum_sim
            api_info.qe_context_sim = context_sim
            api_info.qe_graph_sim = graph_sim

        qa_info_manager.get_api_info_collection().sort_by_qe_sim()

        return qa_info_manager

    def sort_sentence_by_select_part_entity_as_bridge(self, question,
                                                      qa_info_manager,
                                                      weight_context_sim=0.6,
                                                      weight_graph_sim=0.4,
                                                      ):
        self._logger.info(
            "run sort part entity result=%d" % qa_info_manager.get_sentence_size())

        sentence_info_collection = qa_info_manager.get_sentence_info_collection()
        sentence_info_collection.init_vectors(self.kg_models)
        sentence_list = sentence_info_collection.get_entity_list()
        sentence_vec_list = sentence_info_collection.get_entity_context_list()
        sentence_graph_vec_list = sentence_info_collection.get_entity_graph_list()

        question_context_vec = self.kg_models.get_question_entity_vector(question)

        entity_info_collection = qa_info_manager.get_top_related_entity_info_collection()
        entity_list = entity_info_collection.get_entity_list()
        entity_context_vec_list = entity_info_collection.get_entity_context_list()
        entity_graph_vec_list = entity_info_collection.get_entity_graph_list()

        # entity_list, entity_vec_list, entity_graph_vec_list = self.remove_the_not_related_entity_by_only_save_one_for_each(
        #     entity_graph_vec_list=entity_graph_vec_list, entity_vec_list=entity_vec_list, entity_list=entity_list,
        #     question_context_vec=question_context_vec,
        #     qa_info_manager=qa_info_manager
        #
        # )

        qs_context_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                      sentence_vec_list)
        # todo:change to the average graph similarity
        qs_graph_sim = self.get_graph_similarity_by_average_entity_graph_vector(entity_graph_vec_list, question,
                                                                                sentence_graph_vec_list)

        # qs_graph_sim = self.get_query_to_sentence_graph_sim_by_select_top_enttity(entity_graph_vec_list, entity_list,
        #                                                                           entity_vec_list,
        #                                                                           sentence_graph_vec_list,
        #                                                                           sentence_vec_list)

        qs_context_sim = weight_context_sim * qs_context_sim
        qs_graph_sim = weight_graph_sim * qs_graph_sim

        qs_sim = qs_context_sim + qs_graph_sim
        qs_sim = qs_sim.tolist()[0]
        qs_context_sim = qs_context_sim.tolist()[0]
        qs_graph_sim = qs_graph_sim.tolist()[0]

        for sentence_info, sum_sim, sentence, context_sim, graph_sim in zip(sentence_info_collection.sentence_info_list,
                                                                            qs_sim, sentence_list, qs_context_sim,
                                                                            qs_graph_sim):
            sentence_info.qs_sim = sum_sim
            sentence_info.qs_context_sim = context_sim
            sentence_info.qs_graph_sim = graph_sim

        sentence_info_collection.sort_by_qs_sim()

        return qa_info_manager

    def sort_sentences_for_one_api_class(self, question,
                                         qa_info_manager,
                                         sentence_info_collection,
                                         weight_context_sim=0.6,
                                         weight_graph_sim=0.4,
                                         ):

        sentence_info_collection.init_vectors(self.kg_models)
        sentence_list = sentence_info_collection.get_entity_list()
        sentence_vec_list = sentence_info_collection.get_entity_context_list()
        sentence_graph_vec_list = sentence_info_collection.get_entity_graph_list()

        question_context_vec = self.kg_models.get_question_entity_vector(question)

        entity_info_collection = qa_info_manager.get_top_related_entity_info_collection()
        entity_graph_vec_list = entity_info_collection.get_entity_graph_list()

        qs_context_sim = MatrixCalculation.compute_cossin_for_vec_to_matrix_normalize(question_context_vec,
                                                                                      sentence_vec_list)
        qs_graph_sim = self.get_graph_similarity_by_average_entity_graph_vector(entity_graph_vec_list, question,
                                                                                sentence_graph_vec_list)

        qs_context_sim = weight_context_sim * qs_context_sim
        qs_graph_sim = weight_graph_sim * qs_graph_sim

        qs_sim = qs_context_sim + qs_graph_sim
        qs_sim = qs_sim.tolist()[0]
        qs_context_sim = qs_context_sim.tolist()[0]
        qs_graph_sim = qs_graph_sim.tolist()[0]

        for sentence_info, sum_sim, sentence, context_sim, graph_sim in zip(sentence_info_collection.sentence_info_list,
                                                                            qs_sim, sentence_list, qs_context_sim,
                                                                            qs_graph_sim):
            sentence_info.qs_sim = sum_sim
            sentence_info.qs_context_sim = context_sim
            sentence_info.qs_graph_sim = graph_sim

        sentence_info_collection.sort_by_qs_sim()

        return sentence_info_collection

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

        # print("final entity list", len(entity_list), entity_list)
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
            # print("after first removing sim=", sim, "entity=", entity)
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
            # print("final save sim=", entity_info_sumary["sim"], "entity=", entity_info_sumary["entity"])

        return new_entity_list, new_entity_vec_list, new_entity_graph_vec_list

    def filter_the_middle_entity_by_small_similarity_to_question_entity(self, question_context_vec,
                                                                        qa_info_manager):

        node_info_collection = qa_info_manager.get_node_info_collection()
        print("start middle entity num=%d" % node_info_collection.size())

        node_info_collection.fill_each_entity_with_similary_to_question(question_context_vec)
        node_info_collection.sort_by_qe_sim()
        node_info_collection.remove_the_entity_by_qe_similarity()
        qa_info_manager.start_build_top_related_entity_info_list()
        print("after filter middle entity num=%d" % node_info_collection.size())

    def filter_api_entity_the_small_similarity_to_question_entity(self, question_context_vec,
                                                                  qa_info_manager):
        api_info_collection = qa_info_manager.get_api_info_collection()
        print("api info collection before filter size=%r" % api_info_collection.size())
        api_info_collection.fill_each_entity_with_similary_to_question(question_context_vec)
        api_info_collection.sort_by_qe_sim()
        # api_info_collection.remove_the_entity_by_qe_similarity()
        api_info_collection.remove_the_entity_by_save_some_candidate()
        api_info_collection.filter_the_api_by_remove_package()

        print("api info collection after filter size=%r" % api_info_collection.size())

    def get_clean_entity_for_each_word_by_max_n_similarity(self, entity_info_sumary_list,
                                                           word_to_related_entity_list_map):
        clean_entity_kg_id_list = set([])
        print("start get_clean_entity_infi_sumary_list ")
        word_name_entity_mark = {}
        for valid_word, related_entity_list in word_to_related_entity_list_map.items():
            # print("valid word=", valid_word)

            entity_info_list = self.get_first_from_entity_info_sumary_list_and_in_related_entity_list(
                entity_info_sumary_list, related_entity_list, 3)

            # for entity_info in entity_info_list:
            # print("get candidate for word=", valid_word, entity_info_list)
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
            # print("valid word=", valid_word)

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

    def fill_api_id_in_result_list_for_one_sentence_info(self, sentence_info):

        api_entity = self.semanticSearchAccessor.get_api_entity_for_sentence(sentence_info.node_id)
        if api_entity is None:
            return

        sentence_info.api_kg_id = api_entity["id"]
        sentence_info.api_id = api_entity["api_id"]
        sentence_info.api_qualified_name = api_entity["qualified_name"]
        sentence_info.api_kg_id = self.defaultAccessor.get_id_for_node(api_entity)
        sentence_info.api_type = api_entity["api_type"]
        if "api_document_website#1" in dict(api_entity):
            sentence_info.api_document_website = api_entity["api_document_website#1"]

    def fill_api_id_in_result_list(self, result_sentence_list):
        self._logger.info("fill api info for =%d" % len(result_sentence_list))

        for sentence_dict in result_sentence_list:
            api_entity = self.semanticSearchAccessor.get_api_entity_for_sentence(sentence_dict["kg_id"])
            if api_entity is None:
                continue

            sentence_dict["api_kg_id"] = api_entity["id"]
            sentence_dict["api_id"] = api_entity["api_id"]
            sentence_dict["api_qualified_name"] = api_entity["qualified_name"]
            sentence_dict["api_kg_id"] = self.defaultAccessor.get_id_for_node(api_entity)
            sentence_dict["api_type"] = api_entity["api_type"]
            if "api_document_website#1" in dict(api_entity):
                sentence_dict["api_document_website#1"] = api_entity["api_document_website#1"]
        self._logger.info("return result_sentence_list len =%d" % len(result_sentence_list))

        return result_sentence_list

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
