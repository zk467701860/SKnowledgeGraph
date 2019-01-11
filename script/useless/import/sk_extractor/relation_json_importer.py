# -*- coding:utf8 -*-
import sys
import traceback

from py2neo import Relationship

from skgraph.graph.accessor.factory import NodeBuilder
from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient

reload(sys)
sys.setdefaultencoding('utf8')

# neo4j connect
graphClient = DefaultGraphAccessor(GraphClient(server_number=1))
aliasGraphClient = DefaultGraphAccessor(GraphClient(server_number=3))

not_index_property_list = ["Id", "EntityLink", "name", "description"]

not_create_property_list = ["Id", "EntityLink"]


def import_relation_json_list(relation_json_list):
    for relation_json in relation_json_list:
        try:
            import_relation_json(relation_json)
        except Exception:
            traceback.print_exc()


def import_relation_json(relation_json):
    node_id_2_entity_node_map = {}

    entity_list = relation_json["entity_list"]
    for entity_json in entity_list:
        entity_id = entity_json["Id"]
        entity_node = merge_entity_node(entity_json)
        if entity_node != None:
            node_id_2_entity_node_map[entity_id] = entity_node

    relation_json_list = relation_json["relation"]
    for relation_json in relation_json_list:
        merge_relation(node_id_2_entity_node_map, relation_json)


def merge_relation(node_id_2_entity_node_map, relation_json):
    '''

    :param node_id_2_entity_node_map:
    :param relation_json:  et."relation": [
    {
      "subject_id": "0",
      "subject": "java.applet",
      "subject_entity_link": "",
      "object_entity_link": "",
      "relation_type": "provides",
      "object_id": "1",
      "relation_entity_link": "",
      "object": "classes",
      "relation_id": "0"
    },
    :return:
    '''
    subject_node_id = relation_json["subject_id"]
    subject_node = node_id_2_entity_node_map[subject_node_id]

    object_node_id = relation_json["object_id"]
    object_node = node_id_2_entity_node_map[object_node_id]

    relation_type = relation_json["relation_type"]
    if len(relation_type.split()) > 6 or subject_node is None or object_node is None:
        return
    relation_type = relation_type.strip().rstrip('.').rstrip(',').rstrip()
    if object_node["name"] == relation_type:
        return

    if graphClient.get_id_for_node(subject_node) != graphClient.get_id_for_node(object_node):
        graphClient.merge(Relationship(subject_node, relation_type, object_node))


def merge_entity_node(entity_json):
    '''
        entity json example:
        {
            "EntityLink": "",
            "name": "uses to communicate with its applet context . ",
            "description": "uses to communicate with its applet context . ",
            "Id": "2"
        }
        '''
    entity_id = entity_json["Id"]
    if "EntityLink" in entity_json.keys():
        EntityLink = entity_json["EntityLink"]
    else:
        EntityLink = ""
    entity_name = entity_json["name"]

    if entity_name is None or entity_name == "":
        return None
    entity_name = entity_name.strip().rstrip('.').rstrip(',').rstrip()
    entity_json["name"] = entity_name

    entity_node = None

    # 1. find node by entity link
    if EntityLink is not "":
        entity_node = graphClient.find_entity_by_entity_link(EntityLink)

    # 2. find node by name,alias name
    if entity_node is None:
        link_id_node = aliasGraphClient.find_one_by_name_property("alias", entity_name)
        if link_id_node:
            for link_id in link_id_node["link_id"]:
                temp_entity_node = graphClient.find_node_by_id(link_id)
                if temp_entity_node is not None:
                    if temp_entity_node.has_label("api"):
                        if __is_possible_api_name(entity_name):
                            entity_node = temp_entity_node
                            break
                    if temp_entity_node.has_label("wikidata"):
                        entity_node = temp_entity_node
                    if temp_entity_node.has_label("extended knowledge"):
                        entity_node = temp_entity_node
                        break
    if entity_node is None:
        entity_node = getMistakeAddOneWordTypeEntity(entity_name)
    # 3.this is a new entity, create new node for this
    if entity_node is None:
        entity_node = get_new_entity_node_from_entity_json(entity_json)
        graphClient.merge(entity_node)
        entity_node_id = graphClient.get_id_for_node(entity_node)
        create_alias_node_for_entity_node(entity_node, entity_node_id)
    else:
        entity_node = update_entity_node_from_entity_json(entity_node, entity_json)
        graphClient.push(entity_node)
    return entity_node


def get_new_entity_node_from_entity_json(entity_json):
    builder = NodeBuilder().add_entity_label().add_label("extended knowledge")
    for k, v in entity_json.items():
        if k not in not_create_property_list:
            builder = builder.add_one_property(k, v)

    EntityLink = entity_json["EntityLink"]
    if EntityLink != "" and EntityLink.startswith("https://en.wikipedia.org/"):
        builder = builder.add_one_property("site:enwiki", EntityLink)
    return builder.build()


def update_entity_node_from_entity_json(entity_node, entity_json):
    for k, v in entity_json.items():
        if k not in not_index_property_list:
            entity_node[k] = v

    EntityLink = entity_json["EntityLink"]
    if EntityLink != "" and EntityLink.startswith("https://en.wikipedia.org/"):
        entity_node["site:enwiki"] = EntityLink
    return entity_node


def create_alias_node_for_entity_node(node, node_id):
    alias_node = NodeBuilder().add_as_alias().add_one_property("name", node["name"]).build()
    aliasGraphClient.merge(alias_node)
    alias_node_link_id_list = alias_node["link_id"]
    if alias_node_link_id_list is None or alias_node_link_id_list is []:
        alias_node["link_id"] = [node_id]
    else:
        s = set(alias_node_link_id_list)
        s.add(node_id)
        alias_node["link_id"] = list(s)
    aliasGraphClient.push(alias_node)


filter_word_list = ["a", "an", "the", "this", "these", "those"]


def getMistakeAddOneWordTypeEntity(entity_name):
    entity_name_words = entity_name.split()
    if len(entity_name_words) >= 3 and entity_name_words[0].lower() in filter_word_list:
        merge_name = "".join(entity_name_words[1:])
        entity_node = graphClient.find_one_by_name_property(label="extended knowledge", name=merge_name)
        if entity_node:
            entity_node["name"] = " ".join(entity_name_words[1:])
            graphClient.push(entity_node)
            return entity_node
    if len(entity_name_words) >= 2:
        merge_name = "".join(entity_name_words[:])
        entity_node = graphClient.find_one_by_name_property(label="extended knowledge", name=merge_name)
        if entity_node:
            entity_node["name"] = " ".join(entity_name_words[1:])
            graphClient.push(entity_node)
            return entity_node
    return None


def __is_possible_api_name(entity_name):
    if "(" in entity_name or "." in entity_name or "_" in entity_name or entity_name.lower() != entity_name:
        return True
    else:
        return False
