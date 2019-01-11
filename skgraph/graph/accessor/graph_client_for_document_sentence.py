from py2neo import Relationship

from db.model import DocumentSentenceTextAnnotation
from graph_accessor import GraphAccessor
from shared.logger_util import Logger
from skgraph.graph.accessor.factory import NodeBuilder

_logger = Logger("SentenceAccessor").get_log()


class SentenceAccessor(GraphAccessor):
    def update_sentence_type_code(self, sentence_id, sentence_type_code):
        graph = self.get_graph_instance()
        sentence_node = self.find_sentence_node_by_sentence_id(sentence_id)
        if sentence_node is None:
            return
        sentence_node["sentence_type_code"] = sentence_type_code
        graph.push(sentence_node)

    def create_or_update_sentence(self, sentence_id, sentence_text, sentence_type_code):
        graph = self.get_graph_instance()
        sentence_node = self.find_sentence_node_by_sentence_id(sentence_id)
        property_dict = {
            "sentence_id": sentence_id,
            "sentence_text": sentence_text,
            "sentence_type_code": sentence_type_code,
            "sentence_type_string": DocumentSentenceTextAnnotation.get_type_string(sentence_type_code)
        }
        if sentence_node == None:
            builder = NodeBuilder()

            builder = builder.add_entity_label().add_sentence_label().add_property(
                **property_dict)

            node = builder.build()
            graph.create(node)
        else:
            for k, v in property_dict.items():
                sentence_node[k] = v
            graph.push(sentence_node)

    def build_relation_for_sentence_to_api(self, sentence_id, api_id):
        property_name = "source from"
        sentence_node = self.find_sentence_node_by_sentence_id(sentence_id)
        if sentence_node == None:
            return
        api_node = self.find_api_node_by_api_id(api_id)
        if api_node == None:
            return
        relation = Relationship(sentence_node, property_name, api_node)
        self.graph.merge(relation)

    def find_sentence_node_by_sentence_id(self, sentence_id):
        try:
            query = "MATCH (n:sentence{sentence_id:" + str(sentence_id) + "}) return n"
            sentence = self.graph.evaluate(query)

            return sentence
        except Exception, error:
            _logger.exception()
            return None

    def find_api_node_by_api_id(self, api_id):
        try:
            query = "MATCH (n:entity{api_id:" + str(api_id) + "}) return n"
            api_node = self.graph.evaluate(query)

            return api_node
        except Exception, error:
            _logger.exception()
            return None
