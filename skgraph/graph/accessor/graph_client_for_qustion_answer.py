import traceback

from shared.logger_util import Logger
from graph_accessor import GraphAccessor

_logger = Logger("AwesomeGraphAccessor").get_log()


##todo complete this class

class QuestionAndAnswerGraphAccessor(GraphAccessor):
    def __parse_record_list_with_score(self, record_list, node_key='node', score_key='weight'):
        subgraph = None
        score_map = {}
        try:
            for record in record_list:
                node = record[node_key]
                score = record[score_key]
                score_map[str(self.get_id_for_node(node))] = score
                if subgraph is not None:
                    subgraph = subgraph | node
                else:
                    subgraph = node
        except Exception, error:
            _logger.exception()
        return subgraph, score_map

    def __parse_record_list_for_path(self, record_list, path_key='path'):
        subgraph = None
        try:
            for record in record_list:
                path = record[path_key]
                if subgraph is not None:
                    subgraph = subgraph | path
                else:
                    subgraph = path
        except Exception, error:
            _logger.exception()
        return subgraph

    def entity_linking_for_name(self, name, top_number=5):
        '''
        linking a name to a node
        :param name: the name search
        :param top_number: the top number of search result,defalt is top 10
        :return value is a list,each element is a dict d,
        get the node from d['node'],get the score of the result from d['weight']
        '''
        try:
            query = "call apoc.index.search('node name', '{name}', {top_number}) YIELD node, weight return node,weight"
            query = query.format(name=name, top_number=top_number)
            record_list = self.graph.run(query)
            subgraph, score_map = self.__parse_record_list_with_score(record_list, node_key='node', score_key='weight')
            subgraph, score_map = self.__replace_alias_node_to_root_node(subgraph, score_map)
            ## todo add top number limitation
            return subgraph, score_map
        except Exception, error:
            _logger.exception()
            return None, {}

    def __replace_alias_node_to_root_node(self, subgraph, score_map):
        if subgraph is None:
            return None, {}
        nodes = subgraph.nodes()
        for node in nodes:
            if node.has_label('alias'):
                subgraph = subgraph - node
                root_nodes = self.find_root_entity_by_alias_node_in_subgraph(node)
                if root_nodes is not None:
                    subgraph = subgraph | root_nodes

                    alias_node_id_str = str(self.get_id_for_node(node))
                    alias_node_score = score_map[alias_node_id_str]
                    for root_node in root_nodes.nodes():
                        score_map[str(self.get_id_for_node(root_node))] = alias_node_score
        return subgraph, score_map

    def get_what_is_relation_for_id_list_in_subgraph(self, id_list, limit=50):
        relationshipFilter = "'`instance of`>|`subclass of`>'"
        return self.path_expander_for_node_list_for_some_relation_in_subgraph(node_id_list=id_list,
                                                                              relationshipFilter=relationshipFilter,
                                                                              limit=limit)

    def get_what_is_relation_for_subgraph_in_subgraph(self, subgraph):
        '''
        given the subgraph,get all the what is relation for  nodes in this subgraph
        :param subgraph:
        :return:
        '''

        relationshipFilter = "'`instance of`>|`subclass of`>'"
        return self.path_expander_for_nodes_in_subgraph_for_some_relation_in_subgraph(subgraph=subgraph,
                                                                                      relationshipFilter=relationshipFilter)

    def path_expander_for_nodes_in_subgraph_for_some_relation_in_subgraph(self, subgraph, relationshipFilter, limit=50):
        node_id_list = self.parse_subgraph_to_id_set(subgraph)
        return self.path_expander_for_node_list_for_some_relation_in_subgraph(node_id_list, relationshipFilter,
                                                                              limit=limit)

    def path_expander_for_node_list_for_some_relation_in_subgraph(self, node_id_list,
                                                                  relationshipFilter,
                                                                  minDepth=1,
                                                                  maxDepth=1,
                                                                  bfs='false',
                                                                  limit=50):
        label_filter = "'-property'"
        query = "CALL apoc.path.expandConfig([{start_id}],{config}) YIELD path return path"

        config_str = "relationshipFilter:{relationshipFilter},label_filter:{label_filter},minLevel:{minDepth},maxLevel:{maxDepth},bfs:{bfs},limit:{limit}"
        config_str = config_str.format(relationshipFilter=relationshipFilter,
                                       label_filter=label_filter,
                                       minDepth=minDepth,
                                       maxDepth=maxDepth,
                                       bfs=bfs,
                                       limit=str(limit))
        config_str = "{" + config_str + "}"

        node_id_list_str = ",".join([str(node_id) for node_id in node_id_list])
        query = query.format(start_id=node_id_list_str, config=config_str)
        record_list = self.graph.run(query)

        if record_list is not None:
            return self.__parse_record_list_for_path(record_list, path_key='path')
        else:
            return None

    def expand_node_for_directly_adjacent_nodes_to_subgraph_for_all_nodes(self, subgraph, limit=50):
        node_set = subgraph.nodes()
        id_list = self.parse_node_set_to_id_set(node_set)

        record_list = self.path_expander_for_node_list(id_list, limit=limit)
        return self.record_list_to_subgraph(record_list=record_list, key='path')

    def search_api_by_function_description_with_weight(self, description, top_number=20):
        '''

        :param description:
        :param top_number:
        :return: subgraph = None
                weight_map,a map of id string to the search score for the certain node
        '''
        record_list = self.search_api_by_function_description(description, top_number)
        return self.search_result_to_nodes_and_map(record_list)

    def path_expander_for_node_list(self, node_id_list, minDepth=1, maxDepth=1, bfs='false', limit=400):
        query = "match (n) where ID(n) in [{start_id}] match path=(n)-[]-() return path limit {limit}"

        node_id_list_str = ",".join([str(node_id) for node_id in node_id_list])
        query = query.format(start_id=node_id_list_str, limit=limit)
        return self.graph.run(query)

    def remove_all_alias_node_to_root_node(self, subgraph):
        nodes = subgraph.nodes()
        for node in nodes:
            if node.has_label('alias'):
                subgraph = subgraph - node
                root_nodes = self.find_root_entity_by_alias_node_in_subgraph(node)
                if root_nodes:
                    subgraph = subgraph | root_nodes
        return subgraph

    def search_subgraph_by_name_without_alias_node(self, question_text, top_num=20):
        ## todo
        subgraph = self.graphClient.search_nodes_by_name_in_subgraph(question_text, top_num)
        if subgraph == None:
            return None

        subgraph = self.graphClient.remove_all_alias_node_to_root_node(subgraph)
        return subgraph

    def find_root_entity_by_alias_node_in_subgraph(self, node):
        return self.record_list_to_subgraph(self.find_root_entity_by_alias_node(node), 'm')

    def find_root_entity_by_alias_node_id(self, id):
        query = "match (n:alias)-[:alias]-(m) where ID(n)={id} return  m"
        query = query.format(id=id)
        return self.graph.run(query)

    def find_root_entity_by_alias_node(self, node):
        id = self.get_id_for_node(node)
        return self.find_root_entity_by_alias_node_id(id)

    def search_api_by_function_description(self, description, top_number=20):
        '''
        search nodes in graph by node's name
        :param description: the description of the api
        :param top_number: the top number of search result,defalt is top 10
        :return: return value is a list,each element is a dict d,
        get the node from d['node'],get the score of the result from d['weight']
        '''
        query = "call apoc.index.search('function description', '{description}', {top_number}) YIELD node, weight return node,weight"
        query = query.format(description=description, top_number=top_number)
        return self.graph.run(query)

    def get_shortest_path_in_two_node_set_in_subgraph(self, start_node_set, end_node_set, max_degree=8):
        start_id_list = self.parse_node_set_to_id_set(start_node_set)
        end_id_list = self.parse_node_set_to_id_set(end_node_set)

        result = self.get_shortest_path_in_two_id_set(start_id_list, end_id_list, max_degree=max_degree)
        if result:
            return self.record_list_to_subgraph(record_list=result, key='path')
        else:
            return None

    def get_shortest_path_in_two_id_set(self, start_id_list, end_id_list, max_degree=8):
        start_id_set = set(start_id_list)
        end_id_set = set(end_id_list)
        start_id_set = start_id_set - end_id_set
        if len(list(start_id_set)) == 0:
            return None
        query = 'Match path = shortestPath( (n)-[*..{max_degree}]-(m) ) ID(n)  IN[{start_id_set}] and ID(m)  IN[{end_id_set}] RETURN distinct path'

        start_id_set_str = ",".join([str(id) for id in start_id_set])
        end_id_set_str = ",".join([str(id) for id in end_id_set])

        query = query.format(start_id_set=start_id_set_str, end_id_set=end_id_set_str,
                             max_degree=max_degree)
        return self.graph.run(query)

    def parse_node_set_to_id_set(self, node_set):
        id_list = []
        for node in node_set:
            id_list.append(self.get_id_for_node(node))
        return id_list

    def parse_subgraph_to_id_set(self, subgraph):
        return self.parse_node_set_to_id_set(subgraph.nodes())

    def record_list_to_subgraph(self, record_list, key):
        subgraph = None
        try:
            for record in record_list:
                if subgraph is not None:
                    subgraph = subgraph | record[key]
                else:
                    subgraph = record[key]
        except Exception, error:
            traceback.print_exc()
        return subgraph

    def search_result_to_nodes_and_map(self, search_result, node_key='node', weight_key='weight'):
        subgraph = None
        weight_map = {}
        try:
            for record in search_result:
                if subgraph is not None:
                    subgraph = subgraph | record[node_key]
                    weight_map[str(self.get_id_for_node(record[node_key]))] = record[weight_key]
                else:
                    subgraph = record[node_key]
                    weight_map[str(self.get_id_for_node(record[node_key]))] = record[weight_key]

        except Exception, error:
            traceback.print_exc()
        return subgraph, weight_map
