from factory import NodeBuilder
from shared.logger_util import Logger
from graph_accessor import GraphAccessor

_logger = Logger("SOTagGraphAccessor").get_log()


class SOTagGraphAccessor(GraphAccessor):
    '''
    GraphAccessor for Stack Overflow Tags
    '''

    def find_so_tag_by_url(self, tag_url):
        '''
        get so tag node by so tag url
        :param tag_url: the tag url of the so
        :return: Node or None
        '''
        graph = self.get_graph_instance()
        tag_node = self.get_node_by_so_tag_link(tag_url)
        if tag_node is not None:
            return tag_node
        else:
            server_node = self.find_wikidata_node_by_so_tag_link(tag_url)
            if server_node is not None:
                server_node["Stack Overflow tag url"] = tag_url
                server_node.add_label("so tag")
                server_node.add_label("entity")
                graph.push(server_node)
                return server_node
            else:
                return None

    def create_so_tag_by_url(self, tag_url, name):
        '''
        create so tag by given url and name
        :param tag_url: the url of tag
        :param name: the name of the tag
        :return: the node created or exist in the server
        '''
        graph = self.get_graph_instance()
        tag_node = NodeBuilder().add_label("so tag").add_entity_label().add_one_property("name", name).add_one_property(
            "Stack Overflow tag url", tag_url).build()

        graph.merge(tag_node)
        return tag_node

    def get_node_by_so_tag_link(self, tag_url):
        '''
        get so node by url
        :param tag_url: the url of tag
        :return: the node or None
        '''
        try:
            query = 'match (a:entity{`Stack Overflow tag url`:"' + tag_url + '"}) return a'
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception()
            return None

    def find_wikidata_node_by_so_tag_link(self, tag_url):
        '''
        get the wikidata node with tag_url
        :param tag_url: the url of tag
        :return: the node or None
        '''
        try:
            query = 'match (n:wikidata) where exists(n.`Stack Exchange tag`) and "{link}" in n.`Stack Exchange tag` return n limit 1'
            query = query.format(link=tag_url)
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception()
            return None
