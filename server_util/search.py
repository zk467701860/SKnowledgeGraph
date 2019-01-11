"""
    combine multiply search method, to get a search result.
"""

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor


class SearchUtil:

    def __init__(self, graph_client, api_searcher, api_semantic_search):
        self.graph_accessor = DefaultGraphAccessor(graph_client)
        self.api_searcher = api_searcher
        self.api_semantic_search = api_semantic_search

    def search(self, keywords, top_number):
        qa_info_manager = self.api_semantic_search.search_all_entity_by_fulltext_by_half(keywords, top_number + 20)
        qa_info_manager.start_create_node_info_collection()
        entity_info_collection = qa_info_manager.get_entity_info_collection()
        return entity_info_collection.get_entity_list()[:top_number]
