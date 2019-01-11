from semantic_search.semantic_search_util_for_api import APISentenceLevelSemanticSearch

if __name__ == "__main__":
    searcher = APISentenceLevelSemanticSearch()
    searcher.init()
    result_list = []
    while True:
        query_text = raw_input("please input the query:")
        result_list = searcher.semantic_search(query_text, weight_graph_sim=0.5, weight_context_sim=0.5)
        print result_list
        for rank, result in enumerate(result_list):
            print(rank, "=", result)