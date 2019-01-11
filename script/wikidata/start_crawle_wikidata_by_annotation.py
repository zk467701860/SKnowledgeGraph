# coding=utf-8
import json
import traceback

import gevent
from tagme import title_to_uri

from db.engine_factory import EngineFactory
from db.model import WikidataAnnotation, WikidataAndWikipediaData
from extractor.wikidata.WikiDataItem import WikiDataItem

if __name__ == "__main__":
    session = EngineFactory.create_session()
    wikidata_annotation_list = session.query(WikidataAnnotation).all()

    step = 10
    start_id = 0
    end_id = len(wikidata_annotation_list)

    for temp_start_id in range(start_id, end_id, step):
        print("start id=%d", temp_start_id)
        temp_end_id = min(temp_start_id + step, end_id)
        jobs = []
        item_list = []
        for index in range(temp_start_id, temp_end_id):
            annotation = wikidata_annotation_list[index]

            property_wd_item_id = annotation.wd_item_id

            wikidata_and_wikipedia_data = session.query(WikidataAndWikipediaData).filter(
                WikidataAndWikipediaData.wd_item_id == property_wd_item_id).first()

            if wikidata_and_wikipedia_data and WikiDataItem.is_valid_json_string(
                    wikidata_and_wikipedia_data.data_json) == True:
                continue
            item = WikiDataItem(property_wd_item_id, init_at_once=False)
            jobs.append(gevent.spawn(item.init_wikidata_item, property_wd_item_id))
            item_list.append((item, wikidata_and_wikipedia_data))
        gevent.joinall(jobs, timeout=10)
        for (item, wikidata_and_wikipedia_data) in item_list:
            try:
                if item.is_init == False:
                    continue
                url = None
                title = item.get_en_wiki_title()
                if title:
                    url = title_to_uri(title)

                item_data_json_string = json.dumps(item.source_wd_dict_json)

                if wikidata_and_wikipedia_data == None:
                    data_item = WikidataAndWikipediaData(wd_item_id=item.wd_item_id, wd_item_name=item.get_en_name(),
                                                         data_json=item_data_json_string, wikipedia_title=title,
                                                         wikipedia_url=url, wikipedia_text=None)
                    data_item.find_or_create(session=session, autocommit=False)
                else:
                    wikidata_and_wikipedia_data.data_json = item_data_json_string

            except Exception:
                traceback.print_exc()
        session.commit()
