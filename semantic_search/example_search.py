import traceback

from semantic_search_util import SentenceLevelSemanticSearch

if __name__ == "__main__":
    searcher = SentenceLevelSemanticSearch()
    searcher.init()
    result_list = []
    query_text = "Sometimes while creating the socket, i found that the port which was used by the same thread before, is not getting released on close() of the socket. So i tried like this:The problem is , it is not reaching to the second line also. in the first line itself i am getting the expcetion BindException: Address already in use. Is there any way to release the port ?"
    try:
        result_list = searcher.semantic_search(query_text)
    except Exception:
        traceback.print_exc()

    for result in result_list:
        print(result)
