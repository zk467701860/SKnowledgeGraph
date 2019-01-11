import codecs
import json

from py2neo import Relationship

from skgraph.graph.accessor.graph_accessor import GraphClient, DefaultGraphAccessor
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor
from skgraph.graph.accessor.graph_client_for_wikipedia import WikipediaGraphAccessor
from shared.logger_util import Logger

_logger = Logger("AwesomeImporter").get_log()

awesomeGraphAccessor = AwesomeGraphAccessor(GraphClient(server_number=0))
wikipediaGraphAccessor = WikipediaGraphAccessor(awesomeGraphAccessor)
defaultGraphAccessor = DefaultGraphAccessor(awesomeGraphAccessor)

baseGraphClient = awesomeGraphAccessor.graph

file_name = "awesome_item_category_related_to_wikipedia_relation_list.json"
with codecs.open(file_name, 'r', 'utf-8') as f:
    relation_list = json.load(f)
for tag_relation in relation_list:
    start_entity_name = tag_relation["start_entity_name"]
    relation = tag_relation["relation"]
    end_url = tag_relation["end_url"]
    start_node = awesomeGraphAccessor.find_awesome_cate_by_name(start_entity_name)
    end_node = defaultGraphAccessor.get_node_by_wikipedia_link(end_url)
    if end_node is None:
        end_node = wikipediaGraphAccessor.create_wikipedia_item_entity_by_url(end_url)
    if start_node is not None and end_node is not None:
        baseGraphClient.merge(Relationship(start_node, relation, end_node))
        _logger.info("create or merge relation" + str(tag_relation))
    else:
        _logger.warn("fail create relation" + str(tag_relation))
