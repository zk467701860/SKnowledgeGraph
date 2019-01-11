from shared.logger_util import Logger
from skgraph.graph.accessor.graph_accessor import GraphAccessor

_logger = Logger("QAGraphAccessor").get_log()


class QAGraphAccessor(GraphAccessor):
    def entity_linking_by_fulltext_search(self, name, top_number=50):
        """
        linking a name to a node
        :param name: the name search
        :param top_number: the top number of search result,defalt is top 10
        :return value is a list,each element is a dict d,
        get the node from d['node'],get the score of the result from d['weight']
        """
        try:
            query = "call apoc.index.search('entity', '{name}', {top_number}) YIELD node, weight return node,weight"
            query = query.format(name=name, top_number=top_number)
            record_list = self.graph.run(query)
            result_tuple = []
            for record in record_list:
                result_tuple.append({"node": record["node"], "weight": record["weight"]})

            return result_tuple
        except Exception, error:
            _logger.exception("parameters=%r", name)
            return []

    def entity_linking_by_name_search(self, name, top_number=50):
        """
        linking a name to a node
        :param name: the name search
        :param top_number: the top number of search result,defalt is top 10
        :return value is a list,each element is a dict d,
        get the node from d['node'],get the score of the result from d['weight']
        """
        try:
            query = "MATCH(n{name:'"+name+"'}) RETURN n LIMIT " + str(top_number)
            record_list = self.graph.run(query)
            result_tuple = []
            for record in record_list:
                result_tuple.append({"node": record["n"], "weight": 1.0})

            return result_tuple
        except Exception, error:
            _logger.exception("parameters=%r", name)
            return []

    def entity_linking_by_function_search(self, function_str, top_number=10):
        """
        linking a name to a node
        :param function_str: the name search
        :param top_number: the top number of search result,defalt is top 10
        :return value is a list,each element is a dict d,
        get the node from d['node'],get the score of the result from d['weight']
        """
        try:
            MIN_CANDIDATE_NUMBER = 20
            result_tuple = []

            if len(result_tuple) < MIN_CANDIDATE_NUMBER:
                team_result_tuple = self.search_library_node_by_awesome_category(function_str, top_number)
                result_tuple.extend(team_result_tuple)

            if len(result_tuple) < MIN_CANDIDATE_NUMBER:
                team_result_tuple = self.search_library_node_by_library_description(function_str, top_number)
                result_tuple.extend(team_result_tuple)

            return result_tuple
        except Exception, error:
            _logger.exception("parameters=%r", function_str)
            return []

    def search_library_node_by_awesome_category(self, function_str, top_number):
        try:
            query = "call apoc.index.search('library_function', '{function}', {top_number}) YIELD node, weight match(library:`awesome item`)-[r:`main category`]-(node) return library,weight"
            query = query.format(function=function_str, top_number=top_number)
            record_list = self.graph.run(query)
            result_tuple = []
            for record in record_list:
                result_tuple.append({"node": record["library"], "weight": record["weight"]})
            return result_tuple

        except Exception, error:
            _logger.exception("parameters=%r", function_str)
            return []

    def search_library_node_by_library_description(self, function_str, top_number):
        try:
            query = "call apoc.index.search('library_description', '{function}', {top_number}) YIELD library, weight return library,weight"
            query = query.format(function=function_str, top_number=top_number)
            record_list = self.graph.run(query)
            result_tuple = []
            for record in record_list:
                result_tuple.append({"node": record["library"], "weight": record["weight"]})
            return result_tuple

        except Exception, error:
            _logger.exception("parameters=%r", function_str)
            return []

    def search_related_entity(self, entity, top_number=10):
        try:
            query = "call apoc.index.search('entity', '{name}', {top_number}) YIELD node, weight MATCH (node)-[]-(end:entity) return end,weight"
            query = query.format(name=entity, top_number=top_number)
            record_list = self.graph.run(query)
            result_tuple = []
            for record in record_list:
                result_tuple.append({"node": record["end"], "weight": 1.0})

            return result_tuple
        except Exception, error:
            _logger.exception("parameters=%r", entity)
            return []

    def search_entity_by_feature(self, feature, top_number=10):
        try:
            query = "MATCH (node:entity) WHERE node.description=~'.* ((?!not).)+ {feature}.*' RETURN node LIMIT {top_number}"
            query = query.format(feature=feature, top_number=top_number)
            record_list = self.graph.run(query)
            result_tuple = []
            for record in record_list:
                result_tuple.append({"node": record["node"], "weight": 1.0})
            return result_tuple
        except Exception, error:
            _logger.exception("parameters=%r", feature)
            return []

    def search_entity_by_relation(self, entity, relation, top_number=10):
        try:
            query = "call apoc.index.search('entity', '{name}', {top_number}) YIELD node, weight MATCH (node)-[r:`{relation}`]-(end:entity) return end,weight"
            query = query.format(name=entity, relation=relation, top_number=top_number)
            record_list = self.graph.run(query)
            result_tuple = []
            for record in record_list:
                result_tuple.append({"node": record["end"], "weight": 1.0})
            return result_tuple
        except Exception, error:
            _logger.exception("parameters=%r", entity)
            return []
