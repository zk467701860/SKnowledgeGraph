import codecs
import json

from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor
from shared.logger_util import Logger

_logger = Logger("AwesomeImporter").get_log()

awesomeGraphAccessor = AwesomeGraphAccessor(GraphClient(server_number=0))
baseGraphClient = awesomeGraphAccessor.graph

file_name = "awesome_item_category_relation_list.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    relation_list = json.load(f)
for tag_relation in relation_list:
    start_entity_name = tag_relation["start_entity_name"]
    relation = tag_relation["relation"]
    end_entity_name = tag_relation["end_entity_name"]
    start_node = awesomeGraphAccessor.find_awesome_cate_by_name(start_entity_name)
    end_node = awesomeGraphAccessor.find_awesome_cate_by_name(end_entity_name)
    if start_node is not None and end_node is not None:
        baseGraphClient.merge(Relationship(start_node, relation, end_node))
        _logger.info("create or merge relation" + str(tag_relation))
    else:
        _logger.warn("fail create relation" + str(tag_relation))
