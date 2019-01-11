from extractor import WikiDataItemSelector
from extractor import WikiDataSPARQLWrapper

if __name__ == '__main__':
    '''
    start to add stackoverflow tag entity id from wikidata to id selector
    '''
    selector = WikiDataItemSelector()
    result = WikiDataSPARQLWrapper.get_all_stackoverflow_tag()

    for wd_item_id in result:
        selector.add_wikidata_item(wd_item_id)
    print "add all wikidata entity id for stackoverflow tag"
    for wd_item_id in result:
        selector.add_wikidata_item_family(wd_item_id)
