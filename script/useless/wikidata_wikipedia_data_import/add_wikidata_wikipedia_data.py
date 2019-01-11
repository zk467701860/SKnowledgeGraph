# coding: utf-8

import json
import os
import sys
import codecs
import traceback
import logging

from tagme import title_to_uri
import gzip
import re

sys.path.append('/home/fdse/knowledgeGraph/SKnowledgeGraph')
from db.engine_factory import EngineFactory
from db.model import ClassifiedWikipediaDocumentLR, WikidataAndWikipediaData

emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)


def remove_emoji(text):
    return emoji_pattern.sub(r'', text)


def read_gizp_by_line(file_path):
    step_counter = 0
    line_counter = 0
    wikidata_wikipedia_data_list = []
    with gzip.open(file_path) as f:
        for line in f:
            if line_counter == 0:
                line_counter += 1
                continue
            line_counter += 1
            line = line.decode('unicode-escape')
            if len(line) < 3:
                continue
            line = line[0:-2]
            if line_counter % 5000 == 0:
                logging.info('l_c: ' + str(line_counter))

            try:
                obj_d = json.loads(line)
                wiki_data_title = obj_d['sitelinks']['enwiki']['title']
                wd_item_id = obj_d['id']
                wikipedia_url = title_to_uri(wiki_data_title)
                line = remove_emoji(line)
                line = str(line)
                wikidata_wikipedia_data = get_classified_wiki_doc_lr_by_url(wikipedia_url, score, wd_item_id,
                                                                            wiki_data_title, line)
                if wikidata_wikipedia_data is None:
                    continue
                wikidata_wikipedia_data_list.append(wikidata_wikipedia_data)
                if len(wikidata_wikipedia_data_list) > step:
                    commit_one_step(wikidata_wikipedia_data_list)
                    logging.info('step_counter: ' + str(step_counter))

            except Exception:
                # logging.info('et l_c: ' + str(line_counter))
                continue

        session.commit()


def commit_one_step(wikidata_wikipedia_data_list):
    try:
        session.commit()
        for wikidata_wikipedia_data in wikidata_wikipedia_data_list:
            wikidata_wikipedia_data.find_or_create(session=session, autocommit=False)
        session.commit()
    except Exception:
        traceback.print_exc()


def get_classified_wiki_doc_lr_by_url(wikipedia_url, score, wd_item_id, wd_item_name, data_json):
    classified_wiki_doc_lr = session.query(ClassifiedWikipediaDocumentLR).filter_by(url=wikipedia_url).first()
    if classified_wiki_doc_lr is not None and classified_wiki_doc_lr.score is not None and \
            classified_wiki_doc_lr.score >= score:
        wikidata_wikipedia_data = WikidataAndWikipediaData(wd_item_id=wd_item_id, wd_item_name=wd_item_name,
                                                           wikipedia_url=wikipedia_url,
                                                           wikipedia_title=classified_wiki_doc_lr.title,
                                                           wikipedia_text=classified_wiki_doc_lr.content,
                                                           data_json=data_json)
        return wikidata_wikipedia_data
    else:
        return None


if __name__ == "__main__":
    session = EngineFactory.create_session()
    logging.basicConfig(filename='/home/fdse/knowledgeGraph/knowledgeGraph.log', level=logging.DEBUG)
    step = 50
    score = 0.75
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = '/home/fdse/knowledgeGraph/knowledgeGraph.json.gz'
    read_gizp_by_line(file_path)
