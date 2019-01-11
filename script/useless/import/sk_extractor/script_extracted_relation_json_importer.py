# -*- coding:utf8 -*-
import codecs
import json
import os
import sys
import traceback

from relation_json_importer import import_relation_json_list

reload(sys)
sys.setdefaultencoding('utf8')


def read_json_from_file(file_name):
    # Reading data back
    with codecs.open(file_name, 'r', 'utf-8') as f:
        data = json.load(f)
    return data


start_file_id = 380
end_file_id = 596

json_dir = "relation_json"
for file_id in range(start_file_id, end_file_id):
    un_update_file_name = os.path.join(json_dir, str(
        file_id) + "_relation_extracted_from_fasttext_annotated_simple_annotated_all_description.json")
    update_file_name = os.path.join(json_dir, str(
        file_id) + "_updated_relation_extracted_from_fasttext_annotated_simple_annotated_all_description.json")

    print "process " + str(file_id) + " " + un_update_file_name
    try:
        if os.path.exists(update_file_name):
            data_json = read_json_from_file(update_file_name)
        else:
            data_json = read_json_from_file(un_update_file_name)
        import_relation_json_list(data_json)
    except Exception:
        traceback.print_exc()
