import codecs
import json

from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor
from shared.logger_util import Logger

_logger = Logger("AwesomeImporter").get_log()

awesomeGraphAccessor = AwesomeGraphAccessor(GraphClient(server_number=0))
baseGraphClient = awesomeGraphAccessor.graph

file_name = "awesome_item_belong_relations.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    relation_list = json.load(f)
for relation in relation_list:
    start_url = relation["start_url"]
    relation_str = "main category"
    end_entity_name = relation["end_entity_name"]
    start_node = awesomeGraphAccessor.find_or_create_awesome_item_entity_by_url(start_url)

    end_node = awesomeGraphAccessor.find_or_create_awesome_cate(end_entity_name)
    if start_node is not None and end_node is not None:
        relationship = Relationship(start_node, relation_str, end_node)
        baseGraphClient.merge(relationship)
        _logger.info("create or merge relation" + str(relation))
    else:
        print "--------"

        print start_node
        print end_node
        _logger.warn("fail create relation" + str(relation))
        print "--------"
