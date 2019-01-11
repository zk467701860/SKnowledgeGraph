from db.search import APISearcher
from shared.logger_util import Logger
import json
import ast
import re

API_TYPE = {-1: "API_TYPE_ALL_API_ENTITY", 0: "API_TYPE_UNKNOWN", 1: "API_TYPE_PACKAGE", 2: "API_TYPE_CLASS",
            3: "API_TYPE_INTERFACE", 4: "API_TYPE_EXCEPTION", 5: "API_TYPE_ERROR", 6: "API_TYPE_FIELD",
            7: "API_TYPE_CONSTRUCTOR", 8: "API_TYPE_ENUM_CLASS", 9: "API_TYPE_ANNOTATION",
            10: "API_TYPE_XML_ATTRIBUTE", 11: "API_TYPE_METHOD", 12: "API_TYPE_ENUM_CONSTANTS",
            13: "API_TYPE_PRIMARY_TYPE", 14: "API_TYPE_PARAMETER", 15: "API_TYPE_RETURN_VALUE",
            16: "API_TYPE_EXCEPTION_CONDITION"}

test_list = []
get_list=[]
already_list=[]

class APITree:
    def __init__(self, sentence_list, logger=None):
        self._api_searcher = APISearcher()
        if logger is None:
            self.logger = Logger("TreeView").get_log()
        else:
            self.logger = logger
        self._tree = self.get_api_tree_from_sentence_list(sentence_list)

    @property
    def tree(self):
        return self._tree

    @staticmethod
    def get_api_name_list(name):
        result = re.findall(r'(.*)\((.*)\).*', name, re.IGNORECASE)
        print("cut in piece")
        print(result)
        if len(result) == 0:
            return name, []
        else:
            parameters = result[0][1].split(",")
            return result[0][0]+"()", parameters

    def get_api_tree_from_sentence_list(self, sentence_list):
        api_list = []
        fail_num = 0
        for sentence in sentence_list:
            api_entity = {}
            api_entity["api_id"] = sentence["api_id"]
            api_entity["api_type"] = sentence["api_type"]
            api_entity["api_name"] = sentence["api_qualified_name"]
            api_entity["api_sentence"] = sentence
            if api_entity not in api_list:
                api_list.append(api_entity)
        class_martrix = []
        for api in api_list:
            api_name, parameters = self.get_api_name_list(api["api_name"])
            api_class_list = api_name.split(".")
            class_martrix.append({"api_list": api_class_list, "api_id": api["api_id"], "api_type":api["api_type"],
                                  "api_sentence": api["api_sentence"]})
        root_node = APINode(node_id=0, name="root", desc="The Root Of A Class Tree", parent_id=None, full_name="root")
        tree_list = [dict(root_node)]
        for line in class_martrix:
            parent_node_id = 0
            full_name = ""
            sentence_from_api_full_name = ".".join(line["api_list"])
            sentence_from_api_id = line["api_id"]
            sentence_from_api_type = line["api_type"]
            for class_slice in line["api_list"]:
                if full_name == "":
                    full_name = class_slice
                else:
                    full_name = ".".join([full_name, class_slice])
                node_id = APINode.has_child(class_slice, parent_node_id, tree_list)
                if node_id == -1:
                    node_id = len(tree_list)
                    api_entity = self._api_searcher.search_api_id_by_qualified_name(full_name)
                    if not api_entity:
                        if sentence_from_api_full_name == full_name:
                            # print("============================")
                            print(full_name, sentence_from_api_id, sentence_from_api_type)
                            test_list.append(sentence_from_api_id)
                            api_id = sentence_from_api_id
                            desc = API_TYPE[sentence_from_api_type]
                        else:
                            fail_num += 1
                            # if self.logger:
                            #     self.logger.exception("exception occur in finding api=%s", full_name
                            print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
                            api_id = None
                            desc = API_TYPE[0]
                    else:
                        get_list.append(api_entity[0])
                        desc = API_TYPE[api_entity[1]]
                        api_id = api_entity[0]
                    new_node = APINode(node_id=node_id, name=class_slice, desc=desc, parent_id=parent_node_id,
                                       full_name=full_name, api_id=api_id)
                    tree_list.append(dict(new_node))
                    APINode.add_child(tree_list[parent_node_id], node_id)
                parent_node_id = node_id
            self.insert_sentence_node_into_api_tree(line["api_sentence"], parent_id=parent_node_id, tree_list=tree_list)
        print("*********************************")
        print(fail_num)
        print("*********************************")
        return tree_list

    @staticmethod
    def insert_sentence_node_into_api_tree(sentence, parent_id, tree_list):
        new_sentence = SentenceNode(sentence, len(tree_list), desc="SENTENCE", parent_id=parent_id)
        APINode.insert_node_in_tree(new_sentence, tree_list)


class TreeNode(object):
    def __init__(self, node_id=None, name=None, desc=None, parent_id=None, node_type=None):
        self.id = node_id
        self.name = name
        self.desc = desc
        self.parentId = parent_id
        self.type = node_type

    def __getitem__(self, attr):
        return super(TreeNode, self).__getattribute__(attr)

    def keys(self):
        dict_key = []
        for iter_key in vars(self).iterkeys():
            dict_key.append(iter_key)
        return tuple(dict_key)


class APINode(TreeNode):
    def __init__(self, node_id=None, name=None, desc=None, parent_id=None, full_name=None, api_id=None, kg_id=None):
        super(APINode, self).__init__(node_id, name, desc, parent_id, node_type=0)
        self.full_name = full_name
        self.api_id = api_id
        self.kg_id = kg_id
        self.child = []

    @staticmethod
    def has_child(name, parent_node_id, tree_list):
        for child_id in tree_list[parent_node_id]["child"]:
            if name == tree_list[child_id]["name"]:
                if child_id not in already_list:
                    already_list.append(child_id)
                return child_id
        return -1

    @staticmethod
    def add_child(parent_node, child_id):
        parent_node["child"].append(child_id)

    @staticmethod
    def insert_node_in_tree(node, tree_view):
        if node["id"] not in tree_view[node["parentId"]]["child"]:
            APINode.add_child(tree_view[node["parentId"]],node["id"])
            tree_view.append(dict(node))


class SentenceNode(TreeNode):
    def __init__(self, sentence, node_id=None, desc="SENTENCE", parent_id=None):
        super(SentenceNode, self).__init__(node_id=node_id, name=sentence["text"], desc=desc, parent_id=parent_id, node_type=1)
        self.sentence_id = sentence["sentence_id"]
        self.qs_context_sim = sentence["qs_context_sim"]
        self.qs_graph_sim = sentence["qs_graph_sim"]
        self.qs_sim = sentence["qs_sim"]
        self.from_api_id = sentence["api_id"]

    @staticmethod
    def find_parent_node_by_from_api_id(tree, api_id, sentence):
        parent_id = 0
        for node in tree:
            if "api_id" not in node.keys():
                continue
            elif node["api_id"] == api_id:
                parent_id = node["id"]
        return parent_id


if __name__ == "__main__":
    fail_sentence = [101, 103, 110, 118, 120, 124, 128, 129, 141, 142, 150, 156, 159, 160, 161, 170, 176, 179, 182, 192, 196]
    with open("test.json") as f:
        sentence_list = ast.literal_eval(f.read())
    api_tree = APITree(sentence_list).tree
    print(api_tree)
    print("=================================")
    ss = APISearcher()
    print(test_list)
    print(already_list)
    for id in api_tree[0]["child"]:
        if "sentence_id" in api_tree[id].keys():
            # api = ss.search_api_by_id(api_tree[id]["from_api_id"])
            # print(api)
            print id, api_tree[id]["from_api_id"] in test_list,api_tree[id]["from_api_id"] in get_list