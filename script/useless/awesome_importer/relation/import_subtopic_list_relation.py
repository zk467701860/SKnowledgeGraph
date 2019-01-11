import codecs
import json

from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor
from shared.logger_util import Logger

_logger = Logger("AwesomeImporter").get_log()

awesomeGraphAccessor = AwesomeGraphAccessor(GraphClient(server_number=0))
baseGraphClient = awesomeGraphAccessor.graph

file_name = "subtopic_list_relation.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    relation_list = json.load(f)
for tag_relation in relation_list:
    start_url = tag_relation["start_url"]
    relation = "has " + tag_relation["relation"]
    end_url = tag_relation["end_url"]
    start_node = awesomeGraphAccessor.find_awesome_list_entity(start_url)
    end_node = awesomeGraphAccessor.find_awesome_list_entity(end_url)
    if start_node is not None and end_node is not None:
        baseGraphClient.merge(Relationship(start_node, relation, end_node))
        _logger.info("create or merge relation" + str(tag_relation))
    else:
        _logger.warn("fail create relation" + str(tag_relation))
