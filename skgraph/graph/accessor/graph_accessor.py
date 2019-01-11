#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import traceback

from py2neo import remote, NodeSelection, Subgraph, Graph, Relationship

from db.api_linker import APILinker
from factory import GraphFactory, NodeBuilder
from shared.logger_util import Logger

_logger = Logger("GraphAccessor").get_log()


# todo, change the logger to an optional parameters

class GraphClient:
    def __init__(self, config_file_path=None, server_number=1):
        '''
        init a GraphClient object
        :param config_file_path: the config file path,
        if not given, it will looking for the config path in the same directory
        :param server_number: a number index the server,
        the default server number is 1,
        and 0 is stand for the localhost debug server.
        and -1, create a empty GraphClient
        '''
        self._graph = None
        self._config = {}
        if server_number == -1:
            return
        if config_file_path is None:
            self._graph, self._config = GraphFactory.create_from_default_config(server_number)
        else:
            self._graph, self._config = GraphFactory.create_from_config_file(full_path=config_file_path,
                                                                             server_number=server_number)

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        if isinstance(graph, GraphAccessor):
            self._graph = graph.graph
        else:
            self._graph = None

    @graph.deleter
    def graph(self):
        del self._graph

    def valid(self):
        '''
        check if the GraphAccessor valid
        :return: True, valid; False, not valid
        '''
        if self._graph is None:
            return False
        else:
            return True


class GraphAccessor:
    def __init__(self, graph=None):
        if isinstance(graph, GraphAccessor):
            self._graph = graph.graph
        elif isinstance(graph, GraphClient):
            self._graph = graph.graph
        elif isinstance(graph, Graph):
            self._graph = graph
        else:
            self._graph = None

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        if isinstance(graph, GraphAccessor):
            self._graph = graph.graph
        elif isinstance(graph, GraphClient):
            self._graph = graph.graph
        elif isinstance(graph, Graph):
            self._graph = graph
        else:
            self._graph = None

    @graph.deleter
    def graph(self):
        del self._graph

    def valid(self):
        '''
        check if the GraphAccessor valid
        :return: True, valid; False, not valid
        '''
        if self._graph is None:
            return False
        else:
            return True

    @staticmethod
    def get_id_for_node(node):
        '''
        get the id of one node in graph
        :return: the unique id of the node
        '''

        try:
            return remote(node)._id
        except Exception:
            _logger.exception("try to get id of no remote relation")
            return -1

    @staticmethod
    def is_remote_node(node):
        '''
        judge if the node standing for a remote node
        :return: True, standing a remote node
        '''
        if remote(node) is None:
            return False
        else:
            return True

    @staticmethod
    def is_remote_relation(relation):
        '''
        judge if the relation standing for a remote relation
        :return: True, standing a remote node
        '''
        if remote(relation) is None:
            return False
        else:
            return True

    @staticmethod
    def get_id_for_relation(relation):
        '''
        get the id of one relation in graph
        :return: the unique id of the node
        '''
        try:
            return remote(relation)._id
        except Exception:
            _logger.exception("try to get id of no remote relation")
            return -1

    @staticmethod
    def get_start_id_for_relation(relation):
        '''
        get the id of start node for relation

        :return: the unique id of the node
        '''
        return remote(relation.start_node())._id

    @staticmethod
    def get_end_id_for_relation(relation):
        '''
        get the id of end node for relation
        :return: the unique id of the node
        '''
        return remote(relation.end_node())._id

    def get_graph_instance(self):
        '''
        get a original neo4j client instance in py2neo
        :return: a Graph object in py2neo
        '''
        return self._graph

    def merge_relation(self, start_node, relation_str, end_node):
        '''
        merge a relation to graph, and update the create. And will create log and update some metadata.
        :param start_node:
        :param relation_str:
        :param end_node:
        :return:
        '''
        if start_node is None:
            _logger.warn("fail create relation for start node is None")
            return None
        if end_node is None:
            _logger.warn("fail create relation for end node is None")
            return None
        if not relation_str:
            _logger.warn("fail create relation for empty relation string")
            return None

        relationship = Relationship(start_node, relation_str, end_node)
        self.graph.merge(relationship)
        modify_time = int(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        if "_create_time" not in relationship:
            relationship["_create_time"] = modify_time
            relationship["_modify_version"] = 1
        if "_update_time" not in relationship:
            relationship["_update_time"] = modify_time
            relationship["_modify_version"] = relationship["_modify_version"] + 1

        _logger.info("merge id=%d relation version:%d data:%s", self.get_id_for_node(relationship),
                     relationship["_modify_version"], str(relationship))
        self.graph.push(relationship)
        return relationship

    def merge_node(self, node):
        '''
        merge a node to graph, and update the create. And will create log and update some metadata.
        :param node:
        :return: the node created
        '''
        if node is None:
            _logger.warn("fail create node for start node is None")
            return None

        self.graph.merge(node)
        modify_time = int(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        if "_create_time" not in node:
            node["_create_time"] = modify_time
            node["_modify_version"] = 1
        if "_update_time" not in node:
            node["_update_time"] = modify_time
            node["_modify_version"] = node["_modify_version"] + 1

        _logger.info("merge id=%d relation version:%d data:%s", self.get_id_for_node(node),
                     node["_modify_version"], str(node))
        self.graph.push(node)
        return node

    def push_node(self, node):
        '''
        merge a node to graph, and update the create. And will create log and update some metadata.
        :param node:
        :return: the node created
        '''
        if node is None:
            _logger.warn("fail push node for start node is None")
            return None
        if not self.is_remote_node(node):
            _logger.warn("fail push node for start node is not a remote node %s", str(node))
            return
        # self.graph.merge(node)
        modify_time = int(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        if "_create_time" not in node:
            node["_create_time"] = modify_time
            node["_modify_version"] = 0
        node["_update_time"] = modify_time
        node["_modify_version"] = node["_modify_version"] + 1

        _logger.info("push id=%d node version:%d data:%s", self.get_id_for_node(node),
                     node["_modify_version"], str(node))
        self.graph.push(node)
        return node


class DefaultGraphAccessor(GraphAccessor):
    '''
        A Default GraphAccessor for Client, encapsulating some common query methods.
    '''

    def create(self, subgraph):
        """ Run a :meth:`.Transaction.create` operation within an
        `autocommit` :class:`.Transaction`.

        :param subgraph: a :class:`.Node`, :class:`.Relationship` or other
                       :class:`.Subgraph`
        """
        graph = self.get_graph_instance()
        return graph.create(subgraph)

    def merge(self, subgraph):
        """ Run a :meth:`.Transaction.merge` operation within an
        `autocommit` :class:`.Transaction`.

        :param subgraph: a :class:`.Node`, :class:`.Relationship` or other
                       :class:`.Subgraph` object
        :param label: label on which to match any existing nodes
        :param property_keys: property keys on which to match any existing nodes
        """
        graph = self.get_graph_instance()
        return graph.merge(subgraph)

    def push(self, subgraph):
        """ Push data from one or more entities to their remote counterparts.

        :param subgraph: the collection of nodes and relationships to push
        """
        graph = self.get_graph_instance()
        print "subgraph=", subgraph
        return graph.push(subgraph)

    def find_node_by_id(self, node_id):
        '''
        get a node by id
        :param node_id: the id of node
        :return: the Node object
        '''
        try:
            query = 'MATCH (n:entity) where ID(n)={id} return n'
            query = query.format(id=node_id)
            result = self.graph.evaluate(query)
            if result:
                return result
            else:
                return None
        except Exception, error:
            _logger.exception("-----------")
            return None

    def find_relation_by_id(self, relation_id):
        """
        get a relation by id
        :return: the Relationship object
        """
        try:
            query = 'MATCH ()-[r]-() where ID(r)={id} return r'
            query = query.format(id=relation_id)
            result = self.graph.evaluate(query)
            if result:
                return result
            else:
                return None
        except Exception, error:
            _logger.exception("-----------")
            return None

    def get_max_id_for_node(self):
        '''
        get the max id of Node in the whole graph
        :return: the max id
        '''
        query = 'MATCH (n) return max(ID(n))'
        result = self.graph.evaluate(query)
        return result

    def get_max_id_for_relation(self):
        '''
        get the max id of relation in the whole graph
        :return: the max id
        '''
        query = 'MATCH ()-[n]-() return max(ID(n))'
        result = self.graph.evaluate(query)
        return result

    def get_node_name_by_id(self, node_id):
        '''
        get a name property of node by node ID, the node must has the label--"entity"
        :param node_id: the node ID
        :return: the node's name
        '''
        try:
            query = 'match (a:entity) where ID(a)={id} return a.name'
            query = query.format(id=node_id)
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception("-----------")
            return None

    def find_one_by_name_property(self, label, name):
        '''
        find a node for the name property match
        :param label: the node label
        :param name: the
        :return:
        '''
        try:
            query = 'MATCH (n:`' + label + '`{name:"' + name + '"}) return n limit 1'
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception("-----------")
            return None

    def find_by_name_property(self, label, name, limit=5):
        '''
        find nodes for the name property match
        :param limit: limit return number
        :param label: the node label
        :param name: the
        :return: a list of Node object, may be []
        '''
        try:
            query = 'MATCH (n:`' + label + '`{name:"' + name + '"}) return n limit ' + str(limit)
            record_list = self.graph.run(query)
            nodes = []
            for record in record_list:
                nodes.append(record["n"])
            return nodes
        except Exception, error:
            _logger.exception("-----------")
            return []

    def find_one_by_alias_name_property(self, label, name):
        '''
                return None or a Node match
                :param label:
                :param name:
                :return:
                '''
        try:
            query = 'MATCH (n:`{label}`) where "{name}" in n.alias RETURN n limit 1'.format(label=label, name=name)
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception("-----------")
            return None

    def find_by_alias_name_property(self, label, name):
        '''
        return a array of Node or [], get all the node that name string in the "alias" property
        :param label: the label the nodes must have
        :param name: the name for the alias
        :return:
        '''
        try:
            query = 'MATCH (n:`{label}`) where "{name}" in n.alias RETURN distinct n'.format(label=label, name=name)
            node_list = []
            result = self.graph.run(query)
            for n in result:
                node_list.append(n['n'])
            return node_list
        except Exception, error:
            _logger.exception("-----------")
            return []

    def get_relation_by_relation_id(self, relation_id):
        '''
        get the raltionship of specific id
        :return: the max id
        '''
        query = 'MATCH ()-[n]-() where ID(n)={id} return n'.format(id=relation_id)
        result = self.graph.evaluate(query)
        return result

    def get_node_in_scope(self, start_id, end_id):
        '''
        get node in some id scope
        :param start_id: the start id of the node
        :param end_id:
        :return:
        '''
        condition = 'ID(_)>{start_id} and ID(_)<={end_id}'
        condition = condition.format(start_id=start_id, end_id=end_id)
        selection = NodeSelection(self.graph).where(condition)

        result = []

        for node in selection:
            result.append(node)
        return result

    def get_node_in_scope_with_labels(self, start_id, end_id, *labels):
        '''

        :param start_id:
        :param end_id:
        :param labels: the label of the node
        :return:
        '''
        condition = 'ID(_)>{start_id} and ID(_)<={end_id}'
        condition = condition.format(start_id=start_id, end_id=end_id)
        selection = NodeSelection(self.graph, labels=frozenset(labels)).where(condition)
        result = []
        for node in selection:
            result.append(node)
        return result

    def get_adjacent_node_id_list(self, node_id):
        query = "Match (a)-->(b) where ID(a)={start_id} return ID(b) as id"
        query = query.format(start_id=node_id)
        try:
            idlist = []
            result = self.graph.run(query)
            for n in result:
                idlist.append(n['id'])
            return idlist
        except Exception:
            _logger.exception("-----------")
            return []

    def get_all_relation_nodes(self):
        query = "MATCH (n:wd_property) return n"
        try:
            record_list = self.graph.run(query)
            result_list = []
            for record in record_list:
                result_list.append(record["n"])
            return result_list
        except Exception:
            traceback.print_exc()
            return []

    def get_all_nodes_by_label(self, label):
        query = "Match (n:{label}) return n".format(label=label)
        try:
            record_list = self.graph.run(query)
            result_list = []
            for record in record_list:
                result_list.append(record['n'])
            return result_list
        except Exception:
            traceback.print_exc()
            return []

    def expand_node_for_adjacent_nodes_to_subgraph(self, node_id, limit=40):
        """
        get the directly_adjacent_nodes of one node
        :return: return value is a subgraph
        """
        high_quality_query = "Match (n:entity)-[r]-(m:wikidata) where ID(n)={start_id} return distinct r,n,m limit {limit}"
        high_quality_query = high_quality_query.format(start_id=node_id, limit=limit)
        media_quality_query = "Match (n:entity)-[r]-(m:api) where ID(n)={start_id} return distinct r,n,m limit {limit}"
        media_quality_query = media_quality_query.format(start_id=node_id, limit=limit)
        low_quality_query = "Match (n:entity)-[r]-(m:entity) where ID(n)={start_id} return distinct r,n,m limit {limit}"
        low_quality_query = low_quality_query.format(start_id=node_id, limit=limit)
        try:

            nodes = []
            relationships = []
            # todo speed up this by multiple thread
            record_list_for_all_relation = self.graph.run(high_quality_query)

            for record in record_list_for_all_relation:
                r = record["r"]
                relationships.append(r)
                nodes.append(record["n"])
                nodes.append(record["m"])

            record_list_for_all_relation = self.graph.run(media_quality_query)

            for record in record_list_for_all_relation:
                r = record["r"]
                relationships.append(r)
                nodes.append(record["n"])
                nodes.append(record["m"])

            record_list_for_all_relation = self.graph.run(low_quality_query)

            for record in record_list_for_all_relation:
                r = record["r"]
                relationships.append(r)
                nodes.append(record["n"])
                nodes.append(record["m"])

            if nodes:
                return Subgraph(nodes, relationships)
            else:
                return None
        except Exception:
            traceback.print_exc()
            return None

    def get_min_id_for_labels(self, *labels):
        """
        get the min id of nodes with certain lables
        :param labels: the labels for the node
        :return: the id of the node
        """
        query = "MATCH (n:{labels}) return min(ID(n))"
        labels = ["`" + label + "`" for label in labels]
        labels_str = ":".join(labels)
        query = query.format(labels=labels_str)
        return self.graph.evaluate(query)

    def get_max_id_for_labels(self, *labels):
        """
                get the max id of nodes with certain lables
                :param labels: the labels for the node
                :return: the id of the node
                """
        query = "MATCH (n:{labels}) return max(ID(n))"
        labels = ["`" + label + "`" for label in labels]
        labels_str = ":".join(labels)
        query = query.format(labels=labels_str)
        return self.graph.evaluate(query)

    def search_nodes_by_name(self, name, top_number=10, index_name="entity"):
        """
        search nodes in graph by node's name
        :param index_name: the index name which the conduct the full text search
        :param name: the name search
        :param top_number: the top number of search result,defalt is top 10
        :return:return value is a list,each element is a dict d,
        get the node from d['node'],get the score of the result from d['weight']
        """
        try:
            name = name.replace("(", " ").replace(")", " ")
            query = "call apoc.index.search('{index_name}', '{name}', {top_number}) YIELD node, weight return node,weight"
            query = query.format(index_name=index_name, name=name, top_number=top_number)
            return self.graph.run(query)
        except Exception:
            _logger.exception("-----------")
            return None

    def search_nodes_by_name_in_subgraph(self, name, top_number=10, index_name="entity"):
        '''
                search nodes in graph by node's name,return the nodes in subgraph object,if not found,return none
                :param index_name: the index name which the conduct the full text search
                :param name: the name search
                :param top_number: the top number of search result, default is top 10
                :return a subgraph standing for the search result
        '''
        result = self.search_nodes_by_name(name, top_number, index_name)
        if result:
            nodes = []
            for record in result:
                nodes.append(record["node"])
            if nodes:
                return Subgraph(nodes=nodes)
            else:
                return None
        else:
            return None

    def search_nodes_by_name_in_list(self, name, top_number=10, index_name="entity"):
        """
                search nodes in graph by node's name,return a list
                :param index_name: the index name which the conduct the full text search
                :param name: the name search
                :param top_number: the top number of search result, default is top 10
                :return a subgraph standing for the search result
        """
        result = self.search_nodes_by_name(name, top_number, index_name)
        if result:
            nodes = []
            for record in result:
                nodes.append(record["node"])
            return nodes
        else:
            return []

    def get_relations_between_two_nodes(self, start_id, end_id):
        '''
        get all the relations between two node, two directions are possible, in record list format
        :param start_id: the start node id
        :param end_id: the end node id
        :return: in record list format
        '''
        try:
            query = 'Match (n)-[r]-(m) where ID(n)={start_id} and ID(m)={end_id}  RETURN distinct n,r,m'
            query = query.format(start_id=start_id, end_id=end_id)
            return self.graph.run(query)
        except Exception:
            _logger.exception("-----------")
            return []

    def get_relations_between_two_nodes_in_subgraph(self, start_id, end_id):
        '''
        get the relations between two nodes, for two direction,
        and return result in a subgraph object,but could be Node
        :param start_id: the start id
        :param end_id:
        :return: a Subgraph, could be None
        '''
        try:
            result = self.get_relations_between_two_nodes(start_id, end_id)
            if result:
                nodes = []
                relations = []
                for record in result:
                    relations.append(record["r"])
                    nodes.append(record["n"])
                    nodes.append(record["m"])
                if nodes:
                    return Subgraph(nodes, relations)
                else:
                    return None
            else:
                return None
        except Exception, error:
            _logger.exception("-----------")
            return None

    def count_nodes(self):
        '''
        get the number of the nodes in the graph
        :return: the number of the nodes in the graph
        '''
        query = 'Match (n) RETURN count(n)'
        return self.graph.evaluate(query)

    def count_relations(self):
        '''
        get the number of the nodes in the graph
        :return: the number of the nodes in the graph
        '''
        query = 'MATCH ()-->() RETURN count(*)'
        return self.graph.evaluate(query)

    def count_library_nodes(self):
        '''
        get the number of the nodes in the graph
        :return: the number of the nodes in the graph
        '''
        query = 'Match (n:library) RETURN count(n)'
        library_num = self.graph.evaluate(query)

        query = 'Match (n:`awesome item`) RETURN count(n)'
        awesome_num = self.graph.evaluate(query)

        return library_num + awesome_num

    def count_class_nodes(self):
        '''
        get the number of the nodes in the graph
        :return: the number of the nodes in the graph
        '''
        query = 'Match (n:`api class`) RETURN count(n)'
        return self.graph.evaluate(query)

    def count_method_nodes(self):
        '''
        get the number of the nodes in the graph
        :return: the number of the nodes in the graph
        '''
        query = 'Match (n:`api method`) RETURN count(n)'
        return self.graph.evaluate(query)

    def count_package_nodes(self):
        '''
        get the number of the nodes in the graph
        :return: the number of the nodes in the graph
        '''
        query = 'Match (n:`api package`) RETURN count(n)'
        return self.graph.evaluate(query)

    def count_relation_type(self):
        '''
        get the number of the nodes in the graph
        :return: the number of the nodes in the graph
        '''
        query = 'CALL apoc.meta.stats() yield relTypeCount'
        return self.graph.evaluate(query)

    def get_all_relation_type(self):
        '''
        get all relation type in the graph
        :return: a list of type string
        '''
        try:
            query = "CALL db.relationshipTypes()"
            record_list = self.graph.run(query)
            result = []
            for record in record_list:
                result.append(record["relationshipType"])
            return result
        except Exception, error:
            _logger.exception("-----------")
            return []

    def get_all_label_list(self):
        '''
        get all label type in the graph
        :return: a list of type string
        '''
        try:
            query = "CALL db.labels()"
            record_list = self.graph.run(query)
            result = []
            for record in record_list:
                result.append(record["label"])
            return result
        except Exception, error:
            _logger.exception("-----------")
            return []

    def create_relation_node(self, relation_name):
        '''
        create a relation by name
        :param relation_name: the relation name
        :return: the relation created or None
        '''
        if relation_name:
            node = NodeBuilder().add_label("relation").add_one_property("name", relation_name).build()
            self.graph.merge(node)
            return node
        else:
            return None

    def find_a_node_by_label(self, label):
        try:
            query = 'Match  (n:`{label}`) return n limit 1'.format(label=label)
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception("-----------")
            return None

    def get_all_connection_edge_by_id(self, id):
        try:
            query = 'match(a:entity)-[n:connect]->(b:entity) where a.link_id = {id} return n.count,b'
            query = query.format(id=id)
            result = self.graph.run(query)
            return result
        except Exception, error:
            _logger.exception("-----------")
            return []

    def find_outward_relation_by__id(self, id):
        # todo remove this method to a subclass of accessor
        query = 'match (a:entity)-[n]->(b:entity) where id(a) = {id} return n,b'
        query = query.format(id=id)
        try:
            idlist = []
            result = self.graph.run(query)
            for n in result:
                idlist.append(n)
            return idlist
        except Exception:
            _logger.exception("-----------")
            return []

    def find_out_relation_list(self, id, page_index, page_size=50):
        """
        get the out relation list start form one id
        :param id:
        :param page_index:
        :param page_size:
        :return:
        """

        try:
            relation_list = []
            skip_num = page_index * page_size
            query = 'match (a:entity)-[r]->(b:entity) where id(a) = {id} return a,r,b skip {skip_num} limit 50'
            query = query.format(id=id, skip_num=skip_num)
            result = self.graph.run(query)
            for n in result:
                relation_list.append(n['r'])

            return relation_list
        except Exception:
            _logger.exception("-----------")
            return []

    def find_in_relation_list(self, id, page_index, page_size=50):
        """
                get the in relation list start form one id

        :param id:
        :param page_index:
        :return:
        """
        try:
            relation_list = []
            skip_num = page_index * page_size
            query = 'match (a:entity)<-[r]-(b:entity) where id(a) = {id} return a,r,b skip {skip_num} limit 50'
            query = query.format(id=id, skip_num=skip_num)
            result = self.graph.run(query)
            for n in result:
                relation_list.append(n['r'])

            return relation_list

        except Exception:
            _logger.exception("-----------")
            return []

    def get_node_by_wikipedia_link(self, link):
        try:
            query = 'match (a:entity{`site:enwiki`:"' + link + '"}) return a'
            return self.graph.evaluate(query)
        except Exception, error:
            return None

    def find_entity_by_entity_link(self, entity_link_url):
        if entity_link_url.startswith("http://bigcode.fudan.edu.cn/Entity/"):
            entity_id = entity_link_url.replace("http://bigcode.fudan.edu.cn/Entity/", "")
            entity_id = int(entity_id)
            return self.find_node_by_id(entity_id)

        if entity_link_url.startswith("https://en.wikipedia.org/"):
            return self.get_node_by_wikipedia_link(entity_link_url)

        return None

    def get_shortest_path(self, start_id, end_id, max_degree=6, limit=3):
        '''
        get short path in record list object,the key to extract value is "path"
        :param start_id: the start id of node
        :param end_id: the end id of node
        :param max_degree: the max_degree of the path
        :param limit: the limit path
        :return:record list object,the key to extract value is "path"
        '''
        query = 'Match path = shortestPath((n:entity)-[*..{max_degree}]-(m:entity)) where ID(n)={start_id} and ID(m)={end_id} RETURN distinct path limit {limit}'
        query = query.format(start_id=start_id, end_id=end_id, max_degree=max_degree, limit=limit)

        result = self.graph.run(query)
        return result

    def get_shortest_path_in_subgraph(self, start_id, end_id, max_degree=6, limit=3):
        '''
        get short path in Subgraph object
        :param start_id: the start id of node
        :param end_id: the end id of node
        :param max_degree: the max_degree of the path
        :param limit: the limit path
        :return:Subgraph object, if error, return None
        '''
        try:
            query = 'Match path = shortestPath((n:entity)-[*..{max_degree}]-(m:entity)) where ID(n)={start_id} and ID(m)={end_id} RETURN distinct path limit {limit}'
            query = query.format(start_id=start_id, end_id=end_id, max_degree=max_degree, limit=limit)

            record_list = self.graph.run(query)
            nodes = []
            relations = []

            for record in record_list:
                path = record["path"]
                nodes.extend(path.nodes())
                relations.extend(path.relationships())
            if nodes:
                return Subgraph(nodes, relations)
            else:
                return None
        except Exception:
            _logger.exception("----------")
            return None

    def get_shortest_path_to_name_in_subgraph(self,
                                              start_id,
                                              end_node_name,
                                              max_degree=6,
                                              limit=3,
                                              max_end_node_number=3):
        end_nodes = self.find_by_name_property("entity", name=end_node_name, limit=max_end_node_number)
        total_nodes = []
        total_relations = []

        for node in end_nodes:
            end_id = self.get_id_for_node(node)
            subgraph = self.get_shortest_path_in_subgraph(start_id=start_id, end_id=end_id, max_degree=max_degree,
                                                          limit=limit)
            if subgraph:
                total_nodes.extend(subgraph.nodes())
                total_relations.extend(subgraph.relationships())

        if total_nodes:
            return Subgraph(total_nodes, total_relations)
        else:
            return None

    def get_newest_nodes(self, top_number=5):
        """
        search newest nodes in graph

        :return: value is a list,each element is a dict d,
        get the node from d['node']
        :param top_number: the top number of search result,defalt is top 10
        """
        try:
            query = "MATCH (n:wikidata) where ID(n)>94000 RETURN n limit 10"
            query = query.format(top_number=str(top_number + 10))
            nodes = []
            result = self.graph.run(query)
            for q in result:
                nodes.append(q['n'])

            valid_nodes = []
            for node in nodes:
                if node["name"] is not None and node["name"].startswith("http") == False:
                    valid_nodes.append(node)
                    if len(valid_nodes) >= top_number:
                        break

            return valid_nodes
        except Exception:
            _logger.exception("----------")
            return []

    def get_popular_nodes(self, top_number=5):
        """
        search popular nodes in graph

        :param top_number: the top number of search result,defalt is top 3
        :return:return value is a list,each element is a dict d,
        get the node from d['node']
        """
        popular_nodes = [14399, 49360, 1755, 52628, 21961, 107, 16214, 16771, 3975, 19739]
        try:
            query = "match (n:wikidata) where ID(n) in {id_list} return n"
            query = query.format(id_list=str(popular_nodes))
            nodes = []
            result = self.graph.run(query)
            for q in result:
                nodes.append(q['n'])
                if len(nodes) >= top_number:
                    break

            return nodes
        except Exception:
            _logger.exception("----------")
            return []

    def search_nodes_by_keyword(self, keyword, label='api', top_number=10, index_name="api"):

        try:
            keywords = keyword.split()
            name = ""
            for k in keywords:
                name += (k + "* ")
            name = name.replace("(", " ").replace(")", " ")
            query = "call apoc.index.search('{index_name}', '{name}') YIELD node match (node:`{label}`) return node limit {top_number}"
            query = query.format(index_name=index_name, name=name, top_number=top_number, label=label)
            nodes = []
            result = self.graph.run(query)
            for q in result:
                nodes.append(q['node'])
            return Subgraph(nodes=nodes)
        except Exception:
            _logger.exception("-----------")
            return None

    def search_api_id(self, keyword, label="api", top_number=10, index_name="api"):

        try:
            keywords = keyword.split()
            name = ""
            for k in keywords:
                name += (k + "* ")
            name = name.replace("(", " ").replace(")", " ")
            query = "call apoc.index.search('{index_name}', '{name}') YIELD node match (node:`{label}`) where exists(node.api_id) return node limit {top_number}"
            query = query.format(index_name=index_name, name=name, top_number=top_number, label=label)
            nodes = []
            returns = []
            result = self.graph.run(query)
            for q in result:
                nodes.append(q['node'])
            for n in nodes:
                returns.append({"kg_id": GraphAccessor.get_id_for_node(n), "mysql_id": n['api_id']})
            return returns
        except Exception:
            _logger.exception("-----------")
            return None

    def get_api_entity_map_to_node_id(self, api_id_list):
        try:
            query = "match(n:api) where n.api_id in {api_id_list} return ID(n) as kg_id, n.api_id as mysql_id"
            query = query.format(api_id_list=str(api_id_list))
            record_list = self.graph.run(query)
            result = []
            for r in record_list:
                result.append({"kg_id": r["kg_id"], "mysql_id": r['mysql_id']})

            return result
        except Exception:
            _logger.exception("parameters=%s", str(api_id_list))
            return []

    def get_api_entity_map_to_node(self, api_id_list):
        try:
            query = "match(n:api) where n.api_id in {api_id_list} return n"
            query = query.format(api_id_list=str(api_id_list))
            record_list = self.graph.run(query)
            result = []
            for r in record_list:
                result.append(r["n"])

            sorted_result = []
            for api_id in api_id_list:
                for node in result:
                    if node["api_id"] == api_id:
                        sorted_result.append(node)
                        break
            return sorted_result
        except Exception:
            _logger.exception("parameters=%s", str(api_id_list))
            return []

    def api_linking(self, api_string, top_number, api_type, declaration, parent_api):
        api_linker = APILinker()
        context = {"api_type": api_type, "parent_api": parent_api, "declaration": declaration}
        all_sorted_link_result = api_linker.link(api_string, context)
        return all_sorted_link_result[0:top_number]

    def mysql_id2kg_id(self, mysql_id):
        query = 'match (a:entity) where a.api_id={id} return ID(a) limit 1'
        query = query.format(id=mysql_id)
        try:
            result = self.graph.evaluate(query)
            return result
        except Exception:
            _logger.exception("-----------")
            return None

    def kg_id2mysql_id(self, kg_id):
        query = 'match (a:entity) where ID(a)={id} return a.api_id'
        query = query.format(id=kg_id)
        try:
            result = self.graph.evaluate(query)
            return result
        except Exception:
            _logger.exception("-----------")
            return None

    def create_index(self, create_index_statement):
        try:
            if create_index_statement:
                result = self.graph.evaluate(create_index_statement)
                return result
            return None
        except Exception:
            _logger.exception("-----------")
            return None
