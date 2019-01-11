from factory import NodeBuilder
from graph_accessor import GraphAccessor
from shared.logger_util import Logger

_logger = Logger("AwesomeGraphAccessor").get_log()


def merge_property_dict_to_node(node, property_dict):
    old_property_dict = dict(node)

    alias = []
    if "alias" in old_property_dict.keys():
        alias = old_property_dict["alias"]
    if node["name"] is None:
        if "name" in property_dict.keys() and node["name"] != property_dict["name"]:
            alias.append(property_dict["name"])
            property_dict["name"] = node["name"]
    if "alias" in property_dict.keys():
        property_dict["alias"].extend(alias)
        property_dict["alias"] = list(set(property_dict["alias"]))
    else:
        if alias:
            property_dict["alias"] = alias

    merge_property_dict = dict(old_property_dict, **property_dict)

    for k, v in merge_property_dict.items():
        node[k] = v
    return node


class AwesomeGraphAccessor(GraphAccessor):
    def find_awesome_item_by_url(self, item_url):
        graph = self.get_graph_instance()
        awesome_item_node = self.get_awesome_item_by_url(item_url)
        if awesome_item_node is not None:
            return awesome_item_node
        else:
            server_node = self.find_wikidata_node_by_awesome_item_url(item_url)

            if server_node is not None:
                server_node["url"] = item_url
                server_node.add_label("awesome item")
                server_node.add_label("entity")
                graph.push(server_node)
                return server_node
            else:
                return None

    def get_awesome_item_by_url(self, link):
        try:
            query = 'match (a:entity{`url`:"' + link + '"}) return a'
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception("get_awesome_item_by_url")
            return None

    def find_wikidata_node_by_awesome_item_url(self, link):
        try:
            result_node = self.find_wikidata_by_source_code_repository(link)
            if result_node is None:
                result_node = self.find_wikidata_by_source_code_repository_in_array(link)
            if result_node is None:
                result_node = self.find_wikidata_by_official_website_in_array(link)
            return result_node
        except Exception, error:
            _logger.exception("find_wikidata_node_by_awesome_item_url")
            return None

    def find_wikidata_by_official_website_in_array(self, url):
        try:
            query = 'match (n:wikidata) where exists(n.`official website`) and "{link}" in n.`official website` return n limit 1'
            query = query.format(link=url)
            result_node = self.graph.evaluate(query)
            return result_node
        except Exception, error:
            _logger.exception("find_wikidata_by_official_website_in_array")
            return None

    def find_wikidata_by_source_code_repository(self, url):
        try:
            query = 'match (a:entity{`source code repository`:"' + url + '"}) return a'
            result_node = self.graph.evaluate(query)
            return result_node
        except Exception, error:
            _logger.exception("find_wikidata_by_source_code_repository")
            return None

    def find_wikidata_by_source_code_repository_in_array(self, url):
        try:
            query = 'match (n:wikidata) where exists(n.`source code repository`) and "{link}" in n.`source code repository` return n limit 1'
            query = query.format(link=url)
            result_node = self.graph.evaluate(query)
            return result_node
        except Exception, error:
            _logger.exception("find_wikidata_by_source_code_repository_in_array")
            return None

    def find_or_create_awesome_cate(self, cate):

        cate_node = NodeBuilder().add_label("awesome category").add_entity_label().add_one_property("name",
                                                                                                    cate).build()
        self.graph.merge(cate_node)
        return cate_node

    def find_awesome_cate_by_name(self, name):
        try:
            query = 'match (a:`awesome category`{`name`:"' + name + '"}) return a'
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception("find_awesome_cate_by_name")
            return None

    def find_awesome_list_topic_by_name(self, name):
        try:
            query = 'match (a:`awesome list topic`{`name`:"' + name + '"}) return a'
            return self.graph.evaluate(query)
        except Exception, error:
            _logger.exception("find_awesome_list_topic_by_name")
            return None

    def create_or_update_awesome_list_entity(self, url, property_dict):
        node = self.find_awesome_list_entity(url)
        if node is None:
            node = NodeBuilder().add_entity_label().add_label("awesome list").add_property(**property_dict).build()
            node = self.graph.merge(node)
            _logger.info("create awesome list node" + str(property_dict))

        else:
            node = merge_property_dict_to_node(node, property_dict)
            self.graph.push(node)
            _logger.info("update awesome list node" + str(property_dict))

        return node

    def create_or_update_awesome_item_entity(self, url, property_dict):
        node = self.find_awesome_item_by_url(url)
        if node is None:
            node = NodeBuilder().add_entity_label().add_label("awesome item").add_property(**property_dict).build()
            node = self.merge_node(node)
            _logger.info("create awesome item node" + str(property_dict))
        else:
            node = merge_property_dict_to_node(node, property_dict)
            self.push_node(node)
            _logger.info("update awesome item node" + str(property_dict))

        return node

    def find_or_create_awesome_item_entity_by_url(self, url):
        if url.startswith("http") == False:
            return None
        node = self.find_awesome_item_by_url(url)
        if node is None:
            property_dict = {"name": url, "url": url}

            node = NodeBuilder().add_entity_label().add_label("awesome item").add_property(**property_dict).build()
            self.merge_node(node)
            _logger.info("create awesome item node" + str(property_dict))
        return node

    def find_awesome_list_entity(self, url):
        try:
            query = 'match (a:`awesome list`{`url`:"' + url + '"}) return a'
            result_node = self.graph.evaluate(query)
            return result_node
        except Exception, error:
            _logger.exception("find_awesome_list_entity")
            return None

    def find_awesome_item_entity(self, url):
        try:
            query = 'match (a:`awesome item`{`url`:"' + url + '"}) return a'
            result_node = self.graph.evaluate(query)
            return result_node
        except Exception, error:
            _logger.exception("find_awesome_item_entity")
            return None

    def find_start_by_relation_type_and_end_url(self, relation_type, end_entity_url):
        try:
            query = 'match (n)-[r:' + relation_type + '] -> (:`awesome item`{url:"' + end_entity_url + '"}) return n'
            result_node = self.graph.evaluate(query)
            return result_node
        except Exception, error:
            _logger.exception("find_start_by_relation_type_and_end_url")
            return None

    def merge_awesome_nodes(self, id_list):
        try:
            print str(id_list)
            query = 'match (a) where ID(a) in ' + str(id_list) + ' with collect(a) as nodes\n CALL apoc.refactor.mergeNodes(nodes)\n YIELD node RETURN node'
            result_node = self.graph.evaluate(query)
            return result_node
        except Exception, error:
            _logger.exception("merge_awesome_nodes")
            return None