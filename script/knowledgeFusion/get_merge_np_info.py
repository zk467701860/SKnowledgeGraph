import json

from db.engine_factory import EngineFactory
from db.model import NounPhraseMergeClean, DocumentSentenceText, SentenceToMergeNPEntityRelation, \
    SentenceToParagraphRelation


def get_sentence_list_and_relation_id_by_merge_np_id(merge_np_id):
    data_map = {}
    if merge_np_id is not None:
        sentence_list = []
        sentence_id_list = []
        paragraph_id_list = []
        sentence_to_merge_relation_list = session.query(SentenceToMergeNPEntityRelation).filter_by(
            merge_np_id=merge_np_id).all()
        noun_phrase = session.query(NounPhraseMergeClean.text).filter_by(id=merge_np_id).first()[0]
        if noun_phrase is not None and sentence_to_merge_relation_list is not None:
            for each in sentence_to_merge_relation_list:
                sentence_text = session.query(DocumentSentenceText.text).filter_by(id=each.sentence_id).first()[0]
                paragraph_id = \
                session.query(SentenceToParagraphRelation.paragraph_id).filter_by(sentence_id=each.sentence_id).first()[
                    0]
                if sentence_text is not None and paragraph_id is not None:
                    sentence_id_list.append(each.sentence_id)
                    sentence_list.append(sentence_text)
                    paragraph_id_list.append(paragraph_id)
            data_map.setdefault("merge_np_id", merge_np_id)
            data_map.setdefault("noun_phrase", noun_phrase)
            data_map.setdefault("sentence_id_list", sentence_id_list)
            data_map.setdefault("sentence_list", sentence_list)
            data_map.setdefault("paragraph_id_list", paragraph_id_list)
    return data_map


def pack_all_to_json():
    result = []
    noun_phase_merge_clean_list = session.query(NounPhraseMergeClean).all()
    if noun_phase_merge_clean_list is not None:
        for noun_phase_merge_clean in noun_phase_merge_clean_list:
            print "current np_id is ", noun_phase_merge_clean.id
            print "current noun phrase is ", noun_phase_merge_clean.text
            data_map = get_sentence_list_and_relation_id_by_merge_np_id(noun_phase_merge_clean.id)
            if data_map is not None and len(data_map) > 0:
                result.append(data_map)
        with open('np_data.json', 'w') as outfile:
            json.dump(result, outfile)


if __name__ == "__main__":
    engine = EngineFactory.create_engine_by_schema_name('codehub', echo=False)
    session = EngineFactory.create_session(engine=engine, autocommit=False)
    pack_all_to_json()
