# coding=utf-8
import json

import gevent

from db.engine_factory import EngineFactory
from db.model import WikiDataProperty
from extractor.wikidata.WikiDataItem import WikiDataItem

if __name__ == "__main__":
    session = EngineFactory.create_session()
    step = 10
    start_id = 1
    end_id = 50000
    for start_id in range(start_id, end_id, step):
        print("start id=%d", start_id)
        temp_end_id = start_id + step
        jobs = []
        item_list = []
        for property_wd_item_id in range(start_id, temp_end_id):
            property_wd_item_id = "P" + str(property_wd_item_id)

            item = WikiDataItem(property_wd_item_id, init_at_once=False)
            jobs.append(gevent.spawn(item.init_wikidata_item, property_wd_item_id))
            item_list.append(item)
        gevent.joinall(jobs, timeout=10)
        for item in item_list:
            if item.is_init == False:
                continue
            print(item.get_en_name())
            item_data_json_string =json.dumps(item.source_wd_dict_json)

            property = WikiDataProperty(wd_item_id=item.wd_item_id, property_name=item.get_en_name(),
                                        data_json=item_data_json_string)
            property.find_or_create(session=session, autocommit=True)
