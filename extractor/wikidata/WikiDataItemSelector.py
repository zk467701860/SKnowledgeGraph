import codecs
import json
import os
import random

from WikiDataSPARQLWrapper import WikiDataSPARQLWrapper
from WikiDataEntityIDStorage import WikiDataEntityIDStorage
from shared.logger_util import Logger

_logger = Logger(logger="wikidata_item_id_selector").get_log()


class WikiDataItemSelector:
    wikiDataEntityIDStorage = WikiDataEntityIDStorage()
    seed_property_id_set = set(['P31', 'P279', 'P361', ])
    '''
        'P31',  # instance of
        'P279',  # subclass of
        'P361',  # part of
    '''

    def __init__(self):
        self.logger = _logger
        self.wikiDataEntityIDStorage.load()

        start_deny_id_list_path = os.path.join('.', 'start_deny_id_list.txt')
        if os.path.isfile(start_deny_id_list_path):
            print "start deny id file  exist"
            self.seed_deny_id_set = set(json.load(codecs.open(start_deny_id_list_path, 'r', 'utf-8')))
        else:
            print "start deny id file not exist"
            self.seed_deny_id_set = {'Q15640053', 'Q18199879', 'Q924286', 'Q7574076', 'Q847906', 'Q18325841',
                                     'Q1454986', 'Q2678338',
                                     'Q928830', 'Q735', 'Q12617225', 'Q49008', 'Q223393', 'Q8242', 'Q861716'}

        self.wikiDataEntityIDStorage.add_deny_ids(*self.seed_deny_id_set)
        if self.wikiDataEntityIDStorage.accept_id_set_empty():
            self.__init_selected_item_ids()

    def __init_selected_item_ids(self):
        seed_id_set = [
            'Q28530532',  # type of software
            'Q7397',  # software
            'Q21198',  # computer science
            'Q1301371',  # computer network
        ]
        seed_id_set = set(seed_id_set)
        for id in seed_id_set:
            self.add_wikidata_item_family(id)

    def add_wikidata_item(self, wd_item_id):
        '''only add the wikidata item id to selector'''
        self.wikiDataEntityIDStorage.add_accept_ids(wd_item_id)

    def add_wikidata_item_family(self, wd_item_id):
        if self.wikiDataEntityIDStorage.deny_id_exist(wd_item_id):
            self.remove_wikidata_item_family(wd_item_id=wd_item_id)
            return []
        seed_property_id_set = WikiDataItemSelector.seed_property_id_set

        old_size = self.wikiDataEntityIDStorage.size()

        accept_id_list, deny_id_list = WikiDataSPARQLWrapper.get_all_wikidata_item_id_list_with_property_relation_to_entity_from_property_set(
            wd_item_id=wd_item_id, property_id_list=seed_property_id_set)

        extend_id_list = self.wikiDataEntityIDStorage.add_accept_ids(*accept_id_list)
        if deny_id_list:
            self.wikiDataEntityIDStorage.add_deny_ids(*deny_id_list)
        new_size = self.wikiDataEntityIDStorage.size()

        deta = new_size - old_size

        if deta > 50:
            deta = '***'
        else:
            deta = '---'

        if extend_id_list:
            self.logger.info('for %s update size from %d to %d type %s', wd_item_id, old_size, new_size, deta)
            self.logger.info('for %s import: %s', wd_item_id, ",,".join(extend_id_list))
            return extend_id_list
        else:
            return []

    def remove_wikidata_item_family(self, wd_item_id):
        extend_id_list = []
        seed_property_id_set = WikiDataItemSelector.seed_property_id_set

        old_size = self.wikiDataEntityIDStorage.size()

        accept_id_list, deny_id_list = WikiDataSPARQLWrapper.get_all_wikidata_item_id_list_with_property_relation_to_entity_from_property_set(
            wd_item_id=wd_item_id, property_id_list=seed_property_id_set)
        extend_id_list.extend(accept_id_list)
        extend_id_list.extend(deny_id_list)
        extend_id_list = list(set(extend_id_list))

        self.wikiDataEntityIDStorage.add_deny_ids(*extend_id_list)
        new_size = self.wikiDataEntityIDStorage.size()

        self.logger.info('for %s update size from %d to %d', wd_item_id, old_size, new_size)
        return extend_id_list

    def remove_wikidata_item_families(self, *wd_item_id):
        extend_id_list = []
        for id in wd_item_id:
            try:
                extend_id_list.extend(self.remove_wikidata_item_family(wd_item_id=id))
            except Exception, error:
                self.logger.exception("remove_wikidata_item_families")
        return list(set(extend_id_list))

    def get_wikidata_item_id_list(self):
        return self.wikiDataEntityIDStorage.get_accept_id_list()

    def update_id_set_by_iterations(self):
        iteration_count = 0
        extend_id_list = self.expand_id_set_by_one_iteration()
        random.shuffle(extend_id_list)

        iteration_count = iteration_count + 1
        self.logger.info("end iteration " + str(iteration_count) + " ,expand num=" + str(len(extend_id_list)))

        while extend_id_list:
            extend_id_list = self.expand_id_set_by_one_iteration(id_list=extend_id_list)
            iteration_count = iteration_count + 1
            self.logger.info("end iteration " + str(iteration_count) + " ,expand num=" + str(len(extend_id_list)))
        self.logger.info('no more id to extend')

    def update_id_set_by_limit_iterations(self, max_time=1):
        extend_id_list = []
        for i in range(0, max_time):
            extend_id_list = self.expand_id_set_by_one_iteration(extend_id_list)
            self.logger.info("end iteration " + str(i) + " ,expand num=" + str(len(extend_id_list)))
            if not extend_id_list:
                self.logger.info('no more id to extend')
                return

    def expand_id_set_by_one_iteration(self, id_list=[]):
        old_size = self.wikiDataEntityIDStorage.size()
        if not id_list:
            id_list = self.wikiDataEntityIDStorage.get_accept_id_list()

        random.shuffle(id_list)

        extend_id_list = []
        for id in id_list:
            extend_id_list.extend(self.add_wikidata_item_family(wd_item_id=id))
        new_size = self.wikiDataEntityIDStorage.size()

        deta = new_size - old_size
        if deta > 50:
            deta = '***'
        else:
            deta = '---'
        if new_size != old_size:
            self.logger.info('one-iteration :update size from %d to %d type %s', old_size, new_size, deta)
            return extend_id_list
        else:
            return []
