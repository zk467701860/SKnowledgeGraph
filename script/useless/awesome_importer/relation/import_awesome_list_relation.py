import codecs
import json

from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import GraphClient, DefaultGraphAccessor
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor
from skgraph.graph.accessor.graph_client_for_wikidata import WikiDataGraphAccessor
from skgraph.graph.accessor.graph_client_for_wikipedia import WikipediaGraphAccessor
from shared.logger_util import Logger

_logger = Logger("AwesomeImporter").get_log()

awesomeGraphAccessor = AwesomeGraphAccessor(GraphClient(server_number=0))
defaultGraphAccessor = DefaultGraphAccessor(awesomeGraphAccessor)
wikipediaGraphAccessor = WikipediaGraphAccessor(awesomeGraphAccessor)
wikidataGraphAccessor = WikiDataGraphAccessor(awesomeGraphAccessor)

baseGraphClient = awesomeGraphAccessor.graph


def add_defined_for_relation(relation_json):
    relation_str = relation_json["relation"]
    start_node = None
    end_node = None
    if "end_url" in relation_json:
        end_url = relation_json["end_url"]
        end_node = defaultGraphAccessor.get_node_by_wikipedia_link(end_url)
    if "end_entity_name" in relation_json:
        end_node = awesomeGraphAccessor.find_awesome_list_topic_by_name(relation_json["end_entity_name"])
    if end_node is None:
        end_node = wikipediaGraphAccessor.create_wikipedia_item_entity_by_url(
            relation_json["end_url"])
    if "start_url" in relation_json:
        start_node = awesomeGraphAccessor.find_awesome_list_entity(relation_json["start_url"])
    if start_node is None:
        start_node = awesomeGraphAccessor.find_awesome_cate_by_name(relation_json["start_entity_name"])
    if start_node is not None and end_node is not None:
        relationship = Relationship(start_node, relation_str, end_node)
        baseGraphClient.merge(relationship)
        _logger.info("create or merge relation" + str(relation_json))
    else:
        _logger.warn("fail create relation" + str(relation_json))


def add_belong_to_relation(relation_json):
    start_url = relation_json["start_url"]
    relation_str = "main category"
    end_node = None
    if "end_entity_name" in relation_json:
        end_node = awesomeGraphAccessor.find_awesome_cate_by_name(relation_json["end_entity_name"])

    start_node = awesomeGraphAccessor.find_awesome_list_entity(start_url)

    if start_node is not None and end_node is not None:
        relationship = Relationship(start_node, relation_str, end_node)
        baseGraphClient.merge(relationship)
        _logger.info("create or merge relation" + str(relation_json))
    else:
        _logger.warn("fail create relation" + str(relation_json))


def add_contain_to_relation(relation_json):
    start_url = relation_json["start_url"]
    relation_str = "contain topic"
    end_node = None
    if "end_entity_name" in relation_json:
        end_node = awesomeGraphAccessor.find_awesome_cate_by_name(relation_json["end_entity_name"])

    start_node = awesomeGraphAccessor.find_awesome_list_entity(start_url)

    if start_node is not None and end_node is not None:
        relationship = Relationship(start_node, relation_str, end_node)
        baseGraphClient.merge(relationship)
        _logger.info("create or merge relation" + str(relation_json))
    else:
        _logger.warn("fail create relation" + str(relation_json))


def add_same_as_relation(relation_json):
    start_node = None
    relation_str = "same as"
    end_node = None
    if "start_entity_name" in relation_json:
        start_node = awesomeGraphAccessor.find_awesome_cate_by_name(relation_json["start_entity_name"])

    if "end_url" in relation_json:
        end_node = wikidataGraphAccessor.find_by_url(relation_json["end_url"])

    if start_node is not None and end_node is not None:
        relationship = Relationship(start_node, relation_str, end_node)
        baseGraphClient.merge(relationship)
        _logger.info("create or merge relation" + str(relation_json))
    else:
        _logger.warn("fail create relation" + str(relation_json))


file_name = "awesome_list_relation.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    relation_list = json.load(f)
for relation in relation_list:
    try:
        if relation["relation"] == "defined for" or relation["relation"] == "related to":
            add_defined_for_relation(relation)
        elif relation["relation"] == "belong to":
            add_belong_to_relation(relation)
        elif relation["relation"] == "contain":
            add_contain_to_relation(relation)
        elif relation["relation"] == "same as":
            add_same_as_relation(relation)
        else:
            _logger.warn("fail create relation" + str(relation))
    except Exception:
        print "error--------"
        print relation
