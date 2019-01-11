from semantic_search_util import SentenceLevelSemanticSearch
from skgraph.graph.accessor.graph_client_for_sementic_search import SemanticSearchAccessor
from skgraph.graph.accessor.factory import GraphFactory
from semantic_search.Connected_subgraph import Connected_subgraph
_graph,_config = GraphFactory.create_from_default_config(server_number=4)
import ast
if __name__ == "__main__":
    _graph, _config = GraphFactory.create_from_default_config(server_number=4)
    accessor = SemanticSearchAccessor(_graph)
    with open("data.json") as f:
        sentence_list = ast.literal_eval(f.read())
    print sentence_list
    print "#################"
    result_list=[]
    for item in sentence_list:
        num = accessor.judge_api_class_by_api_id(item["api_kg_id"])
        print(item["api_kg_id"]," ",num)
        if num == 1:
            flag = 0
            for result in result_list:
                if result["api_class"] == item["api_qualified_name"]:
                    flag = 1
                    result["sentences"].append({"api_method": "null", "text": item["text"]})
            if flag == 0:
                result_list.append(
                    {
                        "api_class": item["api_qualified_name"],
                        "sentences": [{"api_method": "null", "text": item["text"]}],
                    }
                )
        elif num == 2:
            class_name = accessor.get_api_class_by_api_id(item["api_kg_id"])
            print class_name
            flag = 0
            for result in result_list:
                if result["api_class"] == class_name:
                    flag = 1
                    result["sentences"].append({"api_method": item["api_qualified_name"], "text": item["text"]})
            if flag == 0:
                result_list.append(
                    {
                        "api_class": class_name,
                        "sentences": [{"api_method": item["api_qualified_name"], "text": item["text"]}]
                    }
                )
        else:
            pass
        print result_list
