import re

from py2neo import Subgraph

from accessor.graph_accessor import GraphAccessor
from skgraph.graph.label_util import LabelUtil
from skgraph.graph.relation_util import RelationUtil


class GraphJsonParser:

    def __init__(self, graph_accessor=None):
        self.EMPTY_GRAPH_RETURN_VALUE = {'nodes': [], 'relations': [], "relation_description": []}
        self.filter = NodeRelationFilter()
        self.nodeCleaner = NodeCleaner()
        self.relationUtil = RelationUtil(graph_accessor=graph_accessor)

    def sort_nodes_by_quality(self, nodes):
        nodes.sort(key=lambda k: (len((k.get('properties').keys())), 0), reverse=True)
        return nodes

    def parse_nodes_in_subgraph_to_public_json(self, subgraph):
        """
        parse node in the Subgraph to to json for front shown
        :param subgraph: the Subgraph object
        :return: a json list object [node1,node2,...],
         if subgraph is None, return []
        """
        if subgraph is None:
            return []

        nodes = self.parse_node_list_to_json(subgraph.nodes())
        nodes = self.sort_nodes_by_quality(nodes)
        return nodes

    def parse_node_to_public_json(self, node):
        """
        parse the node to json for front shown
        :param node: the Node object
        :return: a json fit the format defined with front end, return {} if problem occur
        """
        if not self.filter.check_node_validity(node):
            return {}

        all_property_dict = self.nodeCleaner.clean_node_properties(node)
        r = {
            "id": GraphAccessor.get_id_for_node(node),
            "name": self.nodeCleaner.get_clean_node_name(node),
            'labels': self.nodeCleaner.clean_labels(node),
            "properties": all_property_dict,
            "majority_properties": self.nodeCleaner.get_majority_property_from_all_property_dict(all_property_dict)
        }
        return r

    def parse_relation_to_public_json(self, relation):
        """
        parse the relation to json for front shown
        :param relation: the Relationship object
        :return: a json fit the format defined with front end, return {} if problem occur
        """
        if not self.filter.check_relation_validity(relation):
            return {}

        r = {
            "id": GraphAccessor.get_id_for_node(relation),
            "name": relation.type(),
            "start_id": GraphAccessor.get_start_id_for_relation(relation),
            "end_id": GraphAccessor.get_end_id_for_relation(relation)
        }
        return r

    def parse_subgraph_to_public_json(self, subgraph):
        """
        parse the Subgraph to to json for front shown
        :param subgraph: the Subgraph object
        :return: a json object {'nodes': [xxx], 'relations': [xxx], 'relation_description': [xxx]},
         if subgraph is None, return {'nodes': [], 'relations': [],'relation_description': []}
        """

        if subgraph is None:
            return self.EMPTY_GRAPH_RETURN_VALUE
        if type(subgraph) != Subgraph:
            return self.EMPTY_GRAPH_RETURN_VALUE
        filter_subgraph = self.filter.filter_subgraph(subgraph)
        if filter_subgraph is None:
            return self.EMPTY_GRAPH_RETURN_VALUE

        nodes = self.parse_node_list_to_json(filter_subgraph.nodes())
        relations = self.get_relations_list_json(filter_subgraph.relationships())
        type_list = [r["name"] for r in relations]
        description_json_list = self.relationUtil.get_relation_description_json_list(type_list)
        subgraph_json = {'nodes': nodes,
                         'relations': relations,
                         "relation_description": description_json_list}
        return subgraph_json

    def parse_relation_list_to_public_subgraph_json(self, relation_list):
        """
        parse the Subgraph to to json for front shown
        :param subgraph: the Subgraph object
        :return: a json object {'nodes': [xxx], 'relations': [xxx]},
         if subgraph is None, return {'nodes': [], 'relations': []}
        """

        if relation_list == None or len(relation_list) == 0:
            return self.EMPTY_GRAPH_RETURN_VALUE

        filter_relation_list = self.filter.filter_relations(relation_list)
        if filter_relation_list is None or len(filter_relation_list) == 0:
            return self.EMPTY_GRAPH_RETURN_VALUE

        filter_node_list = set([])
        for r in filter_relation_list:
            filter_node_list.add(r.start_node())
            filter_node_list.add(r.end_node())

        nodes = self.parse_node_list_to_json(filter_node_list)

        relations = self.get_relations_list_json(filter_relation_list)
        type_list = [r["name"] for r in relations]
        description_json_list = self.relationUtil.get_relation_description_json_list(type_list)

        subgraph_json = {'nodes': nodes, 'relations': relations, "relation_description": description_json_list}
        return subgraph_json

    def get_relations_list_json(self, filter_relation_list):
        """
        filter the relation list to legal relation list, including removing relation has the same start node and end node

        :param filter_relation_list:
        :return: relation list json
        """
        filter_relation_list = self.remove_multiply_relations_between_nodes(filter_relation_list)

        return self.parse_relation_list_to_json(filter_relation_list)

    def parse_relations_in_subgraph_to_public_json(self, subgraph):
        """
        parse relationship in the Subgraph to to json for front shown
        :param subgraph: the Subgraph object
        :return: a json list object [relationjson1,relationjson2,...],
         if subgraph is None, return []
        """
        if subgraph is None:
            return []

        relations = self.get_relations_list_json(subgraph.relationships())
        return relations

    def parse_node_list_to_json(self, node_list):
        result_list = []
        for n in node_list:
            team = self.parse_node_to_public_json(n)
            if team != {}:
                result_list.append(team)
        return result_list

    def parse_relation_list_to_json(self, relation_list):
        result_list = []
        for r in relation_list:
            team = self.parse_relation_to_public_json(r)
            if team != {}:
                result_list.append(team)
        return result_list

    def remove_multiply_relations_between_nodes(self, relation_list):
        filter_relations_list = []
        for r in relation_list:
            is_duplicate = False
            for exist_r in filter_relations_list:
                if r.start_node() == exist_r.start_node() and r.end_node() == exist_r.end_node():
                    is_duplicate = True
                    break
                if r.start_node() == exist_r.end_node() and r.end_node() == exist_r.start_node():
                    is_duplicate = True
                    break
            if is_duplicate:
                continue
            filter_relations_list.append(r)

        return filter_relations_list


class NodeCleaner:
    NAME_LIST = ["qualified_name", "labels_en", "domain_entity:name","wikipedia:title", "name"]

    def __init__(self):
        self.labelUtil = LabelUtil()
        self.original_id_pattern = re.compile(r"[PQ][0-9]+")

    def clean_labels(self, node):
        labels = node.labels()
        clean_labels = self.labelUtil.filter_labels_set_to_public_label_string_list(labels)
        return clean_labels

    def get_clean_node_name(self, node):
        for primary_name in NodeCleaner.NAME_LIST:
            if primary_name in node.keys():
                return node[primary_name]

        if node.has_label("sentence"):
            return "Sentence:" + node["sentence_text"][:12] + "..."

        return "UNKNOWN"

    def __clean_for_one_property_pair(self, property_name, property_value):
        # todo fix this property
        if property_name == "sentence_type_string":
            return None
        if property_name == "sentence_type_code":
            if property_value == 1:
                return "sentence type", "functionality"
            if property_value == 2:
                return "sentence type", "directive"
            return "sentence type", "others"
        new_property_name = property_name
        new_property_value = property_value

        if self.labelUtil.is_private_property(property_name):
            return None
        if property_name != 'wd_item_id':
            if self.is_wikidata_original_property(property_name):
                return None
            if type(property_value) == list:
                team_value = " ".join(property_value)
                if self.is_illegal_value(team_value):
                    return None
            else:
                if type(property_value) == str:
                    if self.is_illegal_value(property_value):
                        return None

        if self.is_other_language_property(property_name):
            return new_property_name, new_property_value
        else:
            new_property_name = " ".join(property_name.split("_"))
            new_property_value = property_value

        return new_property_name, new_property_value

    def clean_node_properties(self, node):
        """
        clean a py2neo Node object to a dict,remove unnessary property to publish in public
        :param node: py2noe object
        :return: a dict contain the properties
        """

        property_dict = dict(node)
        clean_property_dict = {}

        for key, value in property_dict.items():
            pair = self.__clean_for_one_property_pair(key, value)
            if pair is None:
                continue
            (key, value) = pair
            clean_property_dict[key] = value

        clean_property_dict["name"] = self.get_clean_node_name(node)
        if "description" not in clean_property_dict.keys() and "descriptions_en" in property_dict.keys():
            clean_property_dict["description"] = property_dict["descriptions_en"]
        return clean_property_dict

    def is_wikidata_original_property(self, key):
        is_wikidata_original_property = self.original_id_pattern.search(key) is not None
        return is_wikidata_original_property

    def is_other_language_property(self, property_name):
        if property_name.startswith("labels_") or property_name.startswith("aliases_") or property_name.startswith(
                "descriptions_"):
            return True
        else:
            return False

    def is_illegal_value(self, value):
        if self.original_id_pattern.search(value) is not None:
            return True
        else:
            return False

    def get_majority_property_from_all_property_dict(self, property_dict):
        majority_property_dict = {}
        for k, v in property_dict.items():
            if k.startswith("labels_"):
                continue
            if k.startswith("GND ID"):
                continue
            if k.startswith("BnF ID"):
                continue
            if k.startswith("Freebase ID"):
                continue
            if k.startswith("JSTOR topic ID"):
                continue
            if k.startswith("PSH ID"):
                continue
            if k.startswith("BabelNet id"):
                continue
            if k.startswith("Library of Congress authority identifier"):
                continue

            if k.startswith("aliases_"):
                continue
            if k.startswith("descriptions_"):
                continue
            if k.startswith("site:"):
                continue
            majority_property_dict[k] = v
        return majority_property_dict


class NodeRelationFilter:
    MAX_WORDS = 5

    def __init__(self):
        self.nodeCleaner = NodeCleaner()

    def check_node_validity(self, node):
        """
        check the validation of one node
        :param node: py2neo.Node
        :return:
        """
        if node is None:
            return False

        if not self.nodeCleaner.get_clean_node_name(node):
            return False

        if self.is_node_need_to_check_name(node):
            name = self.nodeCleaner.get_clean_node_name(node)
            if self.check_node_name_validation(name) == False:
                return False
        return True

    def check_node_name_validation(self, name):
        if not name:
            return False
        if len(name.split(" ")) > NodeRelationFilter.MAX_WORDS:
            return False

        return True

    def is_node_need_to_check_name(self, node):
        labels = node.labels()
        if len(labels) <= 2 and "entity" in labels and "extended knowledge" in labels:
            return True
        return False

    def check_relation_validity(self, relation):
        if relation is None:
            return False
        start_node = relation.start_node()
        if not self.check_node_validity(start_node):
            return False
        end_node = relation.end_node()
        if not self.check_node_validity(end_node):
            return False
        return True

    def filter_subgraph(self, subgraph):
        """

        :param subgraph: subgraph is not None
        :return:
        """
        if subgraph == None:
            return None

        filtered_relations = self.filter_relations(subgraph.relationships())
        filtered_nodes = self.filter_nodes(subgraph.nodes())

        if not filtered_nodes:
            return None

        return Subgraph(nodes=filtered_nodes, relationships=filtered_relations)

    def filter_relations(self, old_relations):
        filtered_relations = []
        for relation in old_relations:
            if self.check_relation_validity(relation):
                filtered_relations.append(relation)

        return filtered_relations

    def filter_nodes(self, old_nodes):
        filtered_nodes = []
        for node in old_nodes:
            if self.check_node_validity(node):
                filtered_nodes.append(node)
        return filtered_nodes
