import codecs
import json
import os

from db.engine_factory import EngineFactory
from db.model import WikidataAnnotation

if __name__ == "__main__":
    session = EngineFactory.create_session()
    annotation_json_list = []
    result_json_file_name = "filter_with_properties_wikidata_software_entity.json.valid"
    file_path = os.path.split(os.path.realpath(__file__))[0] + "/" + result_json_file_name

    with codecs.open(file_path, 'r', encoding='utf8') as f:
        annotation_json_list = json.load(f)
    for annotation in annotation_json_list:
        wd_item_id = annotation["wikidata_id"]
        type = 1
        description = None
        url = None
        name = None
        if "wikidata_description" in annotation.keys():
            description = annotation["wikidata_description"]
        if "wikipedia_url" in annotation.keys():
            url = annotation["wikipedia_url"]
        if "wikidata_name" in annotation.keys():
            name = annotation["wikidata_name"]
        annotation = WikidataAnnotation(wd_item_id, type, description, url, name)
        annotation.find_or_create(session, False)
    session.commit()
