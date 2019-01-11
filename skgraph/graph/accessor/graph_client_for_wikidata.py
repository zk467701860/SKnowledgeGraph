from py2neo import NodeSelector

from graph_accessor import GraphAccessor
from shared.logger_util import Logger

_logger = Logger("WikiDataGraphAccessor").get_log()


class WikiDataGraphAccessor(GraphAccessor):
    def create_or_update_wikidata_node(self, node):
        graph = self.get_graph_instance()
        server_node = None
        if 'wd_item_id' in node.properties.keys():
            server_node = self.find_wikidata_node(wd_item_id=node.properties['wd_item_id'])
        if server_node is None:
            server_node = self.find_wikipedia_node(url=node.properties['site:enwiki'])

        if server_node is None:
            graph.create(node)
        else:
            property_dict = dict(node)
            for k, v in property_dict.items():
                server_node[k] = v
            server_node.clear_labels()
            server_node.update_labels(node.labels())
            graph.push(server_node)

    def remove_wikidata_node(self, wd_item_id):
        node = self.find_wikidata_node(wd_item_id=wd_item_id)
        try:
            if node:
                self.graph.delete(node)
        except Exception, error:
            _logger.exception()
            return None

    def find_wikidata_node(self, wd_item_id):
        try:
            query = "MATCH (n:entity{wd_item_id:'" + wd_item_id + "'}) return n"
            node = self.graph.evaluate(query)
            return node
        except Exception, error:
            _logger.exception()
            return None

    def find_wikipedia_node(self, url):
        try:
            query = "MATCH (n:entity{`site:enwiki`:'" + url + "'}) return n"
            node = self.graph.evaluate(query)
            return node
        except Exception, error:
            _logger.exception()
            return None

    def find_by_name_exactly_match_for_wikidata(self, name):
        try:
            selector = NodeSelector(self.graph)
            return selector.select("wikidata", labels_en=name).first()
        except Exception, error:
            _logger.exception()
            return None

    def find_by_url(self, url):
        if url.startswith("https://www.wikidata.org/"):
            return self.find_wikidata_node(url.split("/")[-1])
        else:
            return None

    def find_all_wikidata_nodes(self):
        try:
            query = "MATCH (n:wikidata) return n"
            record_list = self.graph.run(query)
            result = []
            for record in record_list:
                result.append(record["n"])
            return result
        except Exception, error:
            _logger.exception()
            return []
