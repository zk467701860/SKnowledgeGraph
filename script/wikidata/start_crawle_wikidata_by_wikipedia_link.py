# coding=utf-8
import json
import traceback

import gevent
from tagme import title_to_uri

from db.engine_factory import EngineFactory
from db.model import WikidataAndWikipediaData, ClassifiedWikipediaDocumentLR
from extractor.wikidata.WikiDataItem import WikiDataItem

MIN_SCORE = 0.5

if __name__ == "__main__":

    session = EngineFactory.create_session()
    wikipedia_link_list = session.query(ClassifiedWikipediaDocumentLR).filter(
        ClassifiedWikipediaDocumentLR.score >= MIN_SCORE).all()
    step = 10
    start_id = 0
    end_id = len(wikipedia_link_list)

    for start_id in range(start_id, end_id, step):
        print("start id=%d", start_id)
        temp_end_id = start_id + step
        jobs = []
        item_list = []
        for index in range(start_id, temp_end_id):
            annotation = wikipedia_link_list[index]

            wikipedia_url = annotation.url

            wikidata_and_wikipedia_data = session.query(WikidataAndWikipediaData).filter(
                WikidataAndWikipediaData.wikipedia_url == wikipedia_url).first()

            if wikidata_and_wikipedia_data and WikiDataItem.is_valid_json_string(
                    wikidata_and_wikipedia_data.data_json) == True:
                continue

            if WikidataAndWikipediaData.is_exist_wikipedia_url(session=session, wikipeida_url=wikipedia_url):
                continue
            item = WikiDataItem(None, init_at_once=False)
            jobs.append(gevent.spawn(item.init_wikidata_item_from_wikipedia_url, wikipedia_url))
            item_list.append((item, wikidata_and_wikipedia_data))
        gevent.joinall(jobs, timeout=10)
        for (item, wikidata_and_wikipedia_data) in item_list:
            try:
                if item.is_init == False:
                    continue
                print(item.get_en_name())
                title = item.get_en_wiki_title()
                url = title_to_uri(title)

                item_data_json_string = json.dumps(item.source_wd_dict_json)
                if wikidata_and_wikipedia_data == None:

                    data_item = WikidataAndWikipediaData(wd_item_id=item.wd_item_id, wd_item_name=None,
                                                         data_json=item_data_json_string, wikipedia_title=title,
                                                         wikipedia_url=url, wikipedia_text=None)
                    data_item.find_or_create(session=session, autocommit=False)
                else:
                    wikidata_and_wikipedia_data.data_json = item_data_json_string
            except Exception:
                traceback.print_exc()

        session.commit()
