from py2neo import Relationship

from WikiDataCreator import WikiDataNodeCreator
from WikiDataItem import WikiDataItem
from WikiDataPropertyUtil import PropertyCleanUtil
from shared.logger_util import Logger
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_wikidata import WikiDataGraphAccessor

_logger = Logger("wikidata_node_linker").get_log()


class WikiDataRelationLinker:
    propertyCleanUtil = PropertyCleanUtil()

    def __init__(self, graphClient=None):
        self.propertyCleanUtil.load()
        self.creator = WikiDataNodeCreator(graphClient)
        self.logger = _logger
        self.graphClient = graphClient

    def __get_graph(self):
        if not self.graphClient:
            self.graphClient = WikiDataGraphAccessor(GraphClient(server_number=1))
        return self.graphClient

    def link_relation_for_wikidata_items(self, *wd_item_id_list):
        for wd_item_id in wd_item_id_list:
            try:
                self.link_relation_for_one_wikidata_item(wd_item_id=wd_item_id)
            except Exception, error:
                self.logger.warn('%s has exception', wd_item_id)
                self.logger.exception("-----------")

    def link_relation_for_one_wikidata_item(self, wd_item_id):
        item = WikiDataItem(wd_item_id)
        if item.exist():
            relation_property_name_list = item.get_relation_property_name_list()
            start_node = self.__get_graph().find_wikidata_node(wd_item_id=wd_item_id)
            if not start_node:
                self.logger.warn('%s is not exist when create relation', wd_item_id)
                self.creator.create_item_node_from_WikiDataItem_object(item)
                self.logger.warn('%s id created when create relation', wd_item_id)
                start_node = self.__get_graph().find_wikidata_node(wd_item_id=wd_item_id)
            if start_node:
                self.create_relation_for_wd_item_property(start_node=start_node,
                                                          relation_property_id_list=relation_property_name_list)
                self.logger.info("%s link relation successful", start_node['wd_item_id'])
        else:
            print wd_item_id, ' can not be get!'
            self.logger.warn('%s can not be get!', wd_item_id)

    def link_relation_for_one_wikidata_item_from_init_item(self, item):
        wd_item_id = item.wd_item_id
        if item.exist():
            relation_property_name_list = item.get_relation_property_name_list()
            start_node = self.__get_graph().find_wikidata_node(wd_item_id=wd_item_id)
            if not start_node:
                self.logger.warn('%s is not exist when create relation', wd_item_id)
                self.creator.create_item_node_from_WikiDataItem_object(item)
                self.logger.warn('%s id created when create relation', wd_item_id)
                start_node = self.__get_graph().find_wikidata_node(wd_item_id=wd_item_id)
            if start_node:
                self.create_relation_for_wd_item_property(start_node=start_node,
                                                          relation_property_id_list=relation_property_name_list)
                self.logger.info("%s link relation successful", start_node['wd_item_id'])
        else:
            print wd_item_id, ' can not be get!'
            self.logger.warn('%s can not be get!', wd_item_id)

    def create_relation_for_wd_item_property(self, start_node, relation_property_id_list):
        subgraph = start_node
        for property_id in relation_property_id_list:
            try:
                team_graph = self.build_relation_for_one_property(property_id, start_node)
                if team_graph:
                    subgraph = subgraph | team_graph
            except Exception, error:
                self.logger.warn('-%s- create relation fail for property %s', start_node['wd_item_id'], property_id)
                self.logger.exception('this is an exception message')
        self.__get_graph().graph.create(subgraph)

    def build_relation_for_one_property(self, property_id, start_node):
        property_name = self.propertyCleanUtil.get_property_name(property_id=property_id)
        if not property_name:
            self.logger.warn('create relation fail for %s - property name not exist', property_id)
            return None
        property_value = start_node[property_name]

        new_subgraph = None
        if property_value:
            if type(property_value) == list:
                for wd_item_id in property_value:
                    team_subgraph = self.build_relation_between_two_wk_node(start_node=start_node,
                                                                            property_id=property_id,
                                                                            relation_name=property_name,
                                                                            wd_item_id=wd_item_id)
                    if new_subgraph is None:
                        new_subgraph = team_subgraph
                    else:
                        new_subgraph = new_subgraph | team_subgraph
            elif type(property_value) == str:
                team_subgraph = self.build_relation_between_two_wk_node(start_node=start_node,
                                                                        property_id=property_id,
                                                                        relation_name=property_name,
                                                                        wd_item_id=property_value)
                new_subgraph = team_subgraph
        return new_subgraph

    def build_relation_between_two_wk_node(self, start_node, property_id, relation_name, wd_item_id):
        if str(wd_item_id)[0] != 'Q':
            return None
        end_node = self.__get_graph().find_wikidata_node(wd_item_id=wd_item_id)
        if end_node is None:
            self.creator.create_item_node(wd_item_id=wd_item_id)
            end_node = self.__get_graph().find_wikidata_node(wd_item_id=wd_item_id)
        if end_node is not None:
            end_node.add_label("wall")
            self.__get_graph().graph.push(end_node)
            self.logger.info("create wall node for %s", str(wd_item_id))
            team_subgraph = self.build_relation_for_between_two_node(start_node=start_node,
                                                                     relation_name=relation_name,
                                                                     end_node=end_node,
                                                                     property_id=property_id)
            return team_subgraph
        return None

    @staticmethod
    def build_relation_for_between_two_node(start_node, relation_name, end_node, property_id):
        relation = Relationship(start_node, relation_name, end_node, wd_item_id=property_id)
        return start_node | relation | end_node


if __name__ == '__main__':
    linker = WikiDataRelationLinker()
    linker.link_relation_for_wikidata_items('Q2642722')
