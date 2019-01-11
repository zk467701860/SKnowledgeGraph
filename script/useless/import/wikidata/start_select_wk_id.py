from extractor import WikiDataItemSelector

if __name__ == '__main__':
    '''
    start to select the id related to domain in wikidata
    '''
    selector = WikiDataItemSelector()
    selector.update_id_set_by_iterations()
