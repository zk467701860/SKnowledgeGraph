import codecs
import json
import os

from extractor import WikiDataItemSelector

if __name__ == '__main__':
    '''
    start to remove deny id from start id set
    '''
    selector = WikiDataItemSelector()
    start_deny_id_list_path = os.path.join('.', 'start_deny_id_list.txt')

    if os.path.isfile(start_deny_id_list_path):
        print "start deny id file exist"
        seed_deny_id_set = set(json.load(codecs.open(start_deny_id_list_path, 'r', 'utf-8')))
        for deny_id in seed_deny_id_set:
            selector.remove_wikidata_item_family(wd_item_id=deny_id)
    else:
        print "start deny id file not exist!"
