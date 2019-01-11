from graph_accessor import DefaultGraphAccessor
from shared.logger_util import Logger

_logger = Logger("APIGraphAccessor").get_log()


class APIGraphAccessor(DefaultGraphAccessor):
    """
    a GraphAccessor for API node query
    """

    def get_parameter_nodes_of_method(self, method_node_id):
        """
        get all parameter nodes belong to one method
        :param method_node_id: method node id
        :return: parameter nodes list
        """
        try:
            query = 'Match  (n:`java method parameter`)-[r:`belong to`]->(m:`java method`)  where ID(m)={method_node_id} return distinct n'.format(
                method_node_id=method_node_id)
            node_list = []
            result = self.graph.run(query)
            for n in result:
                node_list.append(n['n'])
            return node_list

        except Exception, error:
            _logger.exception()
            return []

    def get_parent_class_node_for_method_node(self, method_node_id):
        """
                get parent class node that one method belong to
                :param method_node_id: method node id
                :return: class node
                """
        try:
            query = 'Match  (n:`java method`)-[r:`belong to`]->(m:`java class`)  where ID(n)={method_node_id} return m limit 1'.format(
                method_node_id=method_node_id)
            return self.graph.evaluate(query)

        except Exception, error:
            _logger.exception()
            return None

    def get_parent_class_node_for_field_node(self, field_node_id):
        """
        get parent class node that one field node belong to
        :param field_node_id:
        :return: class node
        """
        try:
            query = 'Match  (n:`java field`)-[r:`belong to`]->(m:`java class`)  where ID(n)={field_node_id} return m limit 1'.format(
                field_node_id=field_node_id)
            return self.graph.evaluate(query)

        except Exception, error:
            _logger.exception()
            return None

    def get_parent_api_node_for_api_node(self, api_node_id):
        '''
        get parent class node that one field node belong to
        :param field_node_id:
        :return: class node
        '''
        try:
            query = 'Match  (n:`api`)-[r:`belong to`]->(m:`api`)  where ID(n)={api_node_id} return m limit 1'.format(
                api_node_id=api_node_id)

            return self.graph.evaluate(query)

        except Exception, error:
            _logger.exception()
            return None

    def create_or_update_api_node(self, node, primary_key_name="api_id"):
        graph = self.get_graph_instance()
        server_node = self.find_node_by_api_id(node.properties[primary_key_name])
        if server_node is None:
            graph.create(node)
        else:
            property_dict = dict(node)
            for k, v in property_dict.items():
                server_node[k] = v
            server_node.clear_labels()
            server_node.update_labels(node.labels())
            graph.push(server_node)

    def remove_api_node(self, api_id):
        node = self.find_node_by_api_id(api_id)
        try:
            if node:
                self.graph.delete(node)
        except Exception, error:
            _logger.exception()
            return None

    def find_node_by_api_id(self, api_id):
        """
        get a node by id
        :param api_id: the id of api in mysql
        :return: the Node object
        """
        try:
            query = 'MATCH (n:entity {api_id:' + str(api_id) + '}) return n'
            result = self.graph.evaluate(query)
            return result
        except Exception, error:
            _logger.exception("-----------")
            return None

    def get_all_api_id_and_kg_id_pair(self):

        try:
            query = 'Match (n:`api`) return ID(n) as kg_id,n.api_id as api_id'
            result = self.graph.run(query)
            pair_list = []
            for n in result:
                pair_list.append({"api_id": n["api_id"], "kg_id": n["kg_id"]})
            return pair_list

        except Exception, error:
            _logger.exception()
            return None

    def get_related_class_by_id(self, api_id, jump=3):
        try:
            query = 'match data=(na:api)-[*1..{jump}]-(nb:`api class`) where id(na) = {api_id} return data limit 20'.format(jump=jump, api_id=api_id)
            result = self.graph.run(query)
            return result
        except Exception, e:
            _logger.exception()
            return None