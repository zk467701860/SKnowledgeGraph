#!/usr/bin/python
# -*- coding: utf-8 -*-
from tagme import wiki_title

from WikiDataItem import WikiDataItem
from WikiDataPropertyUtil import PropertyCleanUtil
from shared.logger_util import Logger
from skgraph.graph.accessor.factory import NodeBuilder
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_wikidata import WikiDataGraphAccessor

_logger = Logger(logger="wikidata_node_creator").get_log()


class WikiDataNodeCreator:

    def __init__(self, wikidata_graph_accessor=None, init_property_from_file=True):
        if init_property_from_file:
            self.propertyCleanUtil = PropertyCleanUtil()
            self.propertyCleanUtil.load()
        self.logger = _logger
        self.wikidata_graph_accessor = wikidata_graph_accessor

    def init_property_clean_Util(self, property_name_dict):
        self.propertyCleanUtil = PropertyCleanUtil()
        self.propertyCleanUtil.init_by_outside_source(property_name_dict)

    def create_item_nodes(self, *wd_item_id_list):
        for id in wd_item_id_list:
            try:
                self.create_item_node(id)
            except Exception, error:
                self.logger.warn('%s has exception', id)
                self.logger.exception("-----------")

    def create_item_node(self, wd_item_id):
        item = WikiDataItem(wd_item_id)
        if item.exist():
            property_name_list = item.get_wikidata_item_property_name_list()
            # self.update_property_map(property_name_list)
            item_property_dict = item.get_wikidata_item_property_dict()
            property_dict = self.propertyCleanUtil.replace_property_id(item_property_dict, property_name_list)
            self.create_node_from_dict(property_dict)
        else:
            print(wd_item_id, ' can not be get!')
            self.logger.warn('%s can not be get!', wd_item_id)

    def create_item_node_from_WikiDataItem_object(self, item):
        wd_item_id = item.wd_item_id
        if item.exist():
            property_name_list = item.get_wikidata_item_property_name_list()
            # self.update_property_map(property_name_list)
            item_property_dict = item.get_wikidata_item_property_dict()
            property_dict = self.propertyCleanUtil.replace_property_id(item_property_dict, property_name_list)
            self.create_node_from_dict(property_dict)
        else:
            print(wd_item_id, ' can not be get!')
            self.logger.warn('%s can not be get!', wd_item_id)

    def create_simple_wikipedia_node_from_wikipedia_url(self, url):
        title = wiki_title(url.replace("https://en.wikipedia.org/wiki/", ""))
        if title is None or title == "":
            print(url, ' can not be got title!')
            self.logger.warn('%s can not be get!', url)
            return
        property_dict = {"wikipedia:title": title, "site:enwiki": url}
        self.create_node_from_dict(property_dict)

    def create_property_nodes(self, *wd_item_id_list):
        for id in wd_item_id_list:
            self.create_property_node(id)
        # self.propertyCleanUtil.save()

    def create_property_node(self, wd_item_id):
        item = WikiDataItem(wd_item_id)
        if item.exist():

            property_name_list = item.get_wikidata_item_property_name_list()
            item_property_dict = item.get_wikidata_item_property_dict()
            property_dict = self.propertyCleanUtil.replace_property_id(item_property_dict, property_name_list)

            self.create_node_from_dict(property_dict)
            try:
                self.propertyCleanUtil.add(property_dict['wd_item_id'], property_dict['labels_en'])
            except Exception, error:
                self.logger.warn('-%s- fail for labels_en not exist', wd_item_id)
                self.logger.exception('this is an exception message')
        else:
            self.logger.warn('-%s- fail for wikidata item not exist', wd_item_id)
            print(wd_item_id, ' not exist')

    def update_property_map(self, property_id_list):
        property_id_list = self.propertyCleanUtil.filter_not_in_property_name_list(property_id_list)
        # self.create_property_nodes(*property_id_list)

    @staticmethod
    def get_node_labels(property_dict):
        labels = ['wikidata']
        if property_dict['wd_item_id'][0] == 'P':
            labels.append('wd_property')
            labels.append('relation')
            return labels
        else:
            labels.append('entity')
        return labels

    def create_node_from_dict(self, property_dict):
        graphClient = self.__get_graph_client()

        # labels = WikiDataNodeCreator.get_node_labels(property_dict)
        builder = NodeBuilder()
        builder = builder.add_entity_label().add_label_wikidata().add_label_wikipedia().add_property(**property_dict)

        node = builder.build()
        try:
            graphClient.create_or_update_wikidata_node(node=node)
            if "wd_item_id" in property_dict.keys():
                self.logger.info('create node for wikidata item %s', property_dict['wd_item_id'])
            else:
                self.logger.info('create node for wkipedia item %s', property_dict['site:enwiki'])

        except Exception, error:
            if "wd_item_id" in property_dict.keys():
                self.logger.warn('-%s- fail for create node for wikidata item ', property_dict['wd_item_id'])
                self.logger.exception('this is an exception message')
            else:
                self.logger.info('create node for wkipedia item %s', property_dict['site:enwiki'])
                self.logger.exception('this is an exception message')

    def __get_graph_client(self):
        if not self.wikidata_graph_accessor:
            self.wikidata_graph_accessor = WikiDataGraphAccessor(GraphClient(server_number=0))
        wikidata_accessor = self.wikidata_graph_accessor
        return wikidata_accessor


if __name__ == "__main__":
    wikiDataNodeCreator = WikiDataNodeCreator()
    wikiDataNodeCreator.create_item_node(wd_item_id="Q2642722")
