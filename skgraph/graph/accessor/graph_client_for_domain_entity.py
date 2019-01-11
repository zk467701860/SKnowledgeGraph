from py2neo import Relationship

from graph_accessor import GraphAccessor
from shared.logger_util import Logger
from skgraph.graph.accessor.factory import NodeBuilder

_logger = Logger("SentenceAccessor").get_log()


class DomainEntityAccessor(GraphAccessor):
    def get_all_domain_entity(self):
        try:
            query = "MATCH (n:`domain entity`) return n"
            result = self.graph.run(query)
            node_list = []
            for n in result:
                node_list.append(n['n'])
            return node_list
        except Exception, error:
            _logger.exception("------")
            return []

    def create_entity_to_general_concept_relation(self, entity, wikipedia_entity):
        relation = Relationship(entity, 'may link', wikipedia_entity)
        self.graph.merge(relation)

    def delete_all_domain_entity_to_wikipedia_relation(self):
        try:
            query = "MATCH (n:`domain entity`)-[r:`may link`]-(m:wikipedia) delete r"
            self.graph.run(query)
            print("delete domain entity to wikipedia relation complete")

        except Exception, error:
            _logger.exception("------")
            return None

    def delete_all_api_entity_to_wikipedia_relation(self):
        try:
            query = "MATCH (n:`api`)-[r:`may link`]-(m:wikipedia) delete r"
            self.graph.run(query)
            print("delete api to wikipedia relation complete")

        except Exception, error:
            _logger.exception("------")
            return None

    def delete_all_domain_entity_and_relation(self):
        try:
            query = "MATCH (n:`domain entity`)-[r]-(m:entity) delete r"
            self.graph.run(query)
            print("delete domain entity relation complete")
            query = "MATCH (n:`domain entity`) delete n"
            self.graph.run(query)
            print("delete domain entity complete")

        except Exception, error:
            _logger.exception("------")
            return None

    def create_or_update_domain_entity(self, domain_entity_id, name):
        graph = self.get_graph_instance()
        domain_entity = self.find_domain_entity_node_by_id(domain_entity_id=domain_entity_id)
        property_dict = {
            "domain_entity_id": domain_entity_id,
            "domain_entity:name": name,
        }
        if domain_entity == None:
            builder = NodeBuilder()

            builder = builder.add_entity_label().add_domain_entity_label().add_property(
                **property_dict)

            node = builder.build()
            graph.create(node)
        else:
            for k, v in property_dict.items():
                domain_entity[k] = v
            graph.push(domain_entity)

    def build_relation_for_domain_entity_to_sentence(self, sentence_id, domain_entity_id):
        property_name = "extracted from"
        sentence_node = self.find_sentence_node_by_sentence_id(sentence_id)
        if sentence_node == None:
            return
        domain_entity = self.find_domain_entity_node_by_id(domain_entity_id)

        if domain_entity == None:
            return
        relation = Relationship(domain_entity, property_name, sentence_node)
        self.graph.merge(relation)

    def build_relation_for_domain_entity_to_sentence_with_start_node(self, sentence_id, domain_entity,
                                                                     property_name="extracted from"):
        sentence_node = self.find_sentence_node_by_sentence_id(sentence_id)
        if sentence_node == None:
            return

        if domain_entity == None:
            return
        relation = Relationship(domain_entity, property_name, sentence_node)
        self.graph.merge(relation)

    def find_sentence_node_by_sentence_id(self, sentence_id):
        try:
            query = "MATCH (n:sentence{sentence_id:" + str(sentence_id) + "}) return n"
            sentence = self.graph.evaluate(query)

            return sentence
        except Exception, error:
            _logger.exception()
            return None

    def find_domain_entity_node_by_id(self, domain_entity_id):
        try:
            query = "MATCH (n:entity{domain_entity_id:" + str(domain_entity_id) + "}) return n"
            domain_entity_node = self.graph.evaluate(query)

            return domain_entity_node
        except Exception, error:
            _logger.exception()
            return None

    def find_api_entity_node_by_id(self, api_entity_id):
        try:
            query = "MATCH (n:api{api_id:" + str(api_entity_id) + "}) return n"
            api_entity_node = self.graph.evaluate(query)

            return api_entity_node
        except Exception, error:
            _logger.exception()
            return None
