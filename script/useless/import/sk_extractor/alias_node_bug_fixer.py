# -*- coding:utf8 -*-
import sys
import traceback

from script_extracted_relation_json_importer import read_json_from_file

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient

reload(sys)
sys.setdefaultencoding('utf8')

# neo4j connect
graphClient = DefaultGraphAccessor(GraphClient(server_number=1))
aliasGraphClient = DefaultGraphAccessor(GraphClient(server_number=3))


def fix_relation_json_list(relation_json_list):
    for relation_json in relation_json_list:
        fix_relation_json(relation_json)


def fix_relation_json(relation_json):
    entity_list = relation_json["entity_list"]
    for entity_json in entity_list:
        fix_entity_node(entity_json)


def fix_entity_node(entity_json):
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
    EntityLink = entity_json["EntityLink"]
    entity_name = entity_json["name"]

    entity_node = None

    # 1. find node by entity link
    if EntityLink is not "":
        entity_node = graphClient.find_entity_by_entity_link(EntityLink)
        if entity_node is not None:
            return

    # 2. find node by name,alias name
    if entity_node is None:
        link_id_node = aliasGraphClient.find_one_by_name_property("alias", entity_name)
        if link_id_node:
            link_id = link_id_node["link_id"][0]
            entity_node = graphClient.find_node_by_id(link_id)
            if entity_node is not None:
                if entity_node["name"] == entity_name or (
                                entity_node["alias"] is not None and entity_name in entity_node["alias"]) or (
                                entity_node["aliases_en"] is not None and entity_name in entity_node["aliases_en"]):
                    print "right node"
                else:
                    aliasGraphClient.graph.delete(link_id_node)
                    print "delete wrong link node"
            else:
                try:
                    aliasGraphClient.graph.delete(link_id_node)
                    print "delete no link node node"
                except Exception:
                    traceback.print_exc()
    return entity_node


start_file_id = 1
end_file_id = 2

for file_id in range(start_file_id, end_file_id):
    file_name = str(
        file_id) + "_updated_relation_extracted_from_fasttext_annotated_simple_annotated_all_description.json"
    print "process " + str(file_id) + " " + file_name
    try:
        data_json = read_json_from_file(file_name)
        fix_relation_json_list(data_json)
    except Exception:
        traceback.print_exc()
