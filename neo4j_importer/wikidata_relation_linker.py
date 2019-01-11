from py2neo import Relationship

from shared.logger_util import Logger
from skgraph.graph.accessor.graph_client_for_wikidata import WikiDataGraphAccessor

_logger = Logger("wikidata_node_linker").get_log()


class WDRelationLinker:

    def __init__(self, graph_client):
        self.logger = _logger
        self.wikidata_graph_accessor = WikiDataGraphAccessor(graph_client)
        self.unlink_relation = 0

    def __get_graph(self):
        return self.wikidata_graph_accessor

    def start_link(self):
        wikidata_graph_accessor = self.__get_graph()
        node_list = wikidata_graph_accessor.find_all_wikidata_nodes()
        for node in node_list:
            self.link_relation_for_one_wikidata_node(node)
        print("import link relation complete for %d", len(node_list))

        print("unlink relation number=%d", self.unlink_relation)

    def link_relation_for_wikidata_node_by_wd_item_id(self, wd_item_id):
        wikidata_graph_accessor = self.__get_graph()
        wikidata_node = wikidata_graph_accessor.find_wikidata_node(wd_item_id=wd_item_id)
        self.link_relation_for_one_wikidata_node(wikidata_node)

    def link_relation_for_one_wikidata_node(self, wikidata_node):
        wikidata_graph_accessor = self.__get_graph()
        relation_start_node = wikidata_node
        if wikidata_graph_accessor == None:
            return
        if wikidata_node is None or wikidata_node.has_label("wikidata") == False:
            return
        wd_item_id = wikidata_node["wd_item_id"]
        if wd_item_id == None:
            return
        for (property_name, property_value) in wikidata_node.properties.items():
            if property_name == "wd_item_id":
                continue

            if type(property_value) != str and type(property_value) != unicode and type(property_value) != list:
                continue
            if type(property_value) == str or type(property_value) == unicode:
                self.create_method_for_one_entity_property(relation_start_node, property_name, property_value)
            if type(property_value) == list:
                for item_property_value in property_value:
                    if type(item_property_value) == str or type(item_property_value) == unicode:
                        self.create_method_for_one_entity_property(relation_start_node, property_name,
                                                                   item_property_value)
        print("link done for %s", wd_item_id)

    def create_method_for_one_entity_property(self, relation_start_node, property_name, end_node_wd_item_id):
        wikidata_graph_accessor = self.__get_graph()
        if end_node_wd_item_id[0] != "Q":
            return
        id_string = end_node_wd_item_id[1:]
        if id_string.isalnum() == False:
            return
        relation_end_node = wikidata_graph_accessor.find_wikidata_node(wd_item_id=end_node_wd_item_id)
        if relation_end_node == None:
            self.unlink_relation = self.unlink_relation + 1
            return
        relation = Relationship(relation_start_node, property_name, relation_end_node)
        wikidata_graph_accessor.get_graph_instance().merge(relation)
        print("create relation for %s -%s- %s", relation_start_node["wd_item_id"], property_name, end_node_wd_item_id)
