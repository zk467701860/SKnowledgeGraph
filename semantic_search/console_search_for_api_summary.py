from semantic_search.semantic_search_util_for_api import APISentenceLevelSemanticSearch
from  db.search import SentenceSearcher
from skgraph.graph.accessor.graph_client_for_sementic_search import SemanticSearchAccessor
from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
if __name__ == "__main__":
    api_semantic_searcher = APISentenceLevelSemanticSearch()
    api_semantic_searcher.init()
    result_list = []
    while True:
        query_text = raw_input("please input the query:")
        print("query text type ", type(query_text))
        result_list = api_semantic_searcher.semantic_search_summary_by_api_with_class(query_text=query_text,
                                                                                      weight_graph_sim=0.4,
                                                                                      weight_context_sim=0.6,
                                                                                      )
        final_result_list = []
        client = GraphClient(server_number=4)
        semanticSearchAccessor = SemanticSearchAccessor(client)
        accessor = semanticSearchAccessor
        for rank, sentence_collection in enumerate(result_list):
            all_sentence_infos = sentence_collection.get_all_sentence_infos()
            first_sentence = all_sentence_infos[0].parse_to_json()
            first = SentenceSearcher.search_first_sentence_by_api_id(first_sentence["api_id"])
            if first_sentence["api_type"] == 2 or first_sentence["api_type"] == 3:
                first_class_name = first_sentence["api_qualified_name"]
                method = first_sentence["api_qualified_name"]
            else:
                first_class_name = accessor.get_api_class_by_api_id(first_sentence["api_kg_id"])
                method = first_sentence["api_qualified_name"]
            final_result_list.append(
                {
                    "class_name": first_class_name,
                    "sim": sentence_collection.get_sum_qs_sim(),
                    "sentences": [{"method": method, "text": first_sentence["text"], "first": first}]
                }
            )
            for index in range(1, len(all_sentence_infos)):
                sentence = all_sentence_infos[index].parse_to_json()
                first = SentenceSearcher.search_first_sentence_by_api_id(sentence["api_id"])
                # print "api_name: ", sentence["api_qualified_name"]," ",sentence["api_kg_id"]
                if first_class_name == None:
                    first_class_name = accessor.get_api_class_by_api_id(sentence["api_kg_id"])
                    final_result_list[len(final_result_list) - 1]["class_name"] = first_class_name
                method = sentence["api_qualified_name"]
                final_result_list[len(final_result_list) - 1]["sentences"].append(
                    {"method": method, "text": sentence["text"], "first": first})
            if final_result_list[len(final_result_list) - 1]["class_name"] == None:
                final_result_list[len(final_result_list) - 1]["class_name"] = method
        print final_result_list


        #
        # result_list = searcher.semantic_search_summary_by_api_with_class(query_text, weight_graph_sim=0.4,
        #                                                                  weight_context_sim=0.6)
        # for rank, sentence_collection in enumerate(result_list):
        #     for sentence_info in sentence_collection.get_all_sentence_infos():
        #         print(rank, sentence_collection.get_sum_qs_sim(), sentence_info.api_qualified_name, "=",
        #               sentence_info.parse_to_json())
        # print ("simple version")
        #
        # for rank, sentence_collection in enumerate(result_list):
        #     for sentence_info in sentence_collection.get_all_sentence_infos():
        #         print(rank, sentence_info.api_qualified_name, "=",
        #               sentence_info.sentence_node["sentence_text"]
        #               )
        # print ("**************************")
