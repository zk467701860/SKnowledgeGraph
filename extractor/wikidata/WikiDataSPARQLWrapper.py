from gevent import monkey

monkey.patch_all()
import gevent
from wikidataintegrator import wdi_core


class WikiDataSPARQLWrapper:
    def __init__(self):
        pass

    illegal_name = ["family tree",
                    "duplicated disambiguation page",
                    "Wiktionary redirect",
                    "redirect page"]
    part_name = ["Wiki", "game", "article", " page", "sports", "MediaWiki", "railway", "station", "Metro", "Subway",
                 "genre", "road", "Road", "subway", "Road", "Station"]

    @staticmethod
    def get_all_wikidata_item_id_list_which_has_one_property_relation_to_entity(wd_item_id, property_id):
        query = '''SELECT DISTINCT ?cheval ?chevalLabel WHERE {
             ?cheval wdt:%s* wd:%s.
             SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
           }
           ORDER BY ?cheval''' % (property_id, wd_item_id)
        jobs = [gevent.spawn(wdi_core.WDItemEngine.execute_sparql_query, query)]
        gevent.joinall(jobs, timeout=180)

        json = jobs[0]
        # json = wdi_core.WDItemEngine.execute_sparql_query(query=query)
        return WikiDataSPARQLWrapper.__extract_id_list(json)

    @staticmethod
    def get_all_wikidata_item_id_list_with_property_relation_to_entity_from_property_set(wd_item_id, property_id_list):
        jobs = []
        for property_id in property_id_list:
            query = '''SELECT DISTINCT ?cheval ?chevalLabel WHERE {
                ?cheval wdt:%s* wd:%s.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
              }
              ORDER BY ?cheval''' % (property_id, wd_item_id)
            jobs.append(gevent.spawn(wdi_core.WDItemEngine.execute_sparql_query, query))

        gevent.joinall(jobs, timeout=180)

        accept_id_list = []
        deny_id_list = []
        for job in jobs:
            json = job.value
            team_accept_id_list, team_deny_id_list = WikiDataSPARQLWrapper.__extract_id_list(json)
            accept_id_list.extend(team_accept_id_list)
            deny_id_list.extend(team_deny_id_list)
            print '-*-\n'

        return list(set(accept_id_list)), list(set(deny_id_list))

    @staticmethod
    def get_all_subclass_of_entity(wd_item_id):
        query = '''SELECT DISTINCT ?cheval ?chevalLabel WHERE {
          ?cheval wdt:P279* wd:%s.
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        ORDER BY ?cheval''' % wd_item_id
        json = wdi_core.WDItemEngine.execute_sparql_query(query=query)
        return WikiDataSPARQLWrapper.__extract_id_list(json)

    @staticmethod
    def get_all_instance_of_entity(wd_item_id):
        query = '''SELECT DISTINCT ?cheval ?chevalLabel WHERE {
          ?cheval wdt:P31* wd:%s.
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        ORDER BY ?cheval''' % wd_item_id
        json = wdi_core.WDItemEngine.execute_sparql_query(query=query)
        return WikiDataSPARQLWrapper.__extract_id_list(json)

    @staticmethod
    def __extract_id_list(wd_query_result):
        if not wd_query_result:
            return [], []

        result_list = wd_query_result['results']['bindings']
        accept_id_list = []
        deny_id_list = []
        for item in result_list:
            url = item['cheval']['value']
            name = item['chevalLabel']['value']
            id = url.split('entity/')[1]

            if WikiDataSPARQLWrapper.is_illegal(name):
                deny_id_list.append(id)
            else:
                accept_id_list.append(id)
        return accept_id_list, deny_id_list

    @staticmethod
    def __extract_tag_list(wd_query_result):
        if not wd_query_result:
            return []
        else:
            result_list = wd_query_result['results']['bindings']
            result = []

            for item in result_list:
                url = item['item']['value']
                name = item['itemLabel']['value']
                id = url.split('entity/')[1]
                so_url = item['Stack_Exchange__']['value']
                if "https://stackoverflow.com/tags" in so_url:
                    result.append(id)
            return result

    @staticmethod
    def is_illegal(name):
        for t in WikiDataSPARQLWrapper.part_name:
            if name.find(t) != -1:
                return True

        if name in WikiDataSPARQLWrapper.illegal_name:
            return True
        return False

    @staticmethod
    def get_all_stackoverflow_tag():
        query = '''SELECT ?item ?itemLabel ?Stack_Exchange__ WHERE {
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        OPTIONAL { ?item wdt:P1482 ?Stack_Exchange__. }
        }
        '''
        json = wdi_core.WDItemEngine.execute_sparql_query(query=query)
        return WikiDataSPARQLWrapper.__extract_tag_list(json)


if __name__ == '__main__':
    '''
    id_list, deny_list = WikiDataSPARQLWrapper.get_all_wikidata_item_id_list_with_property_relation_to_entity_from_property_set(
        wd_item_id='Q7397', property_id_list=['P31', 'P279', 'P361'])
    print 'accept=', id_list
    print 'deny=', deny_list
    '''
    result = WikiDataSPARQLWrapper.get_all_stackoverflow_tag()
    print result
