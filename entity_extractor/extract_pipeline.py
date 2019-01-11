# coding=utf-8

from db.engine_factory import EngineFactory
from db.model import DocumentSentenceText
from db.model import NounPhraseMergeClean, NounPhraseMergeCleanFromNPRelation, NounPhrase, \
    NounPhraseExtractFromDocumentRelation, NounPhraseExtractFromSentenceRelation, SentenceToMergeNPEntityRelation
from entity_extractor.extractor import EntityExtractor


class CandidateEntityExtractionPipeline:
    def __init__(self):
        self.extractor = EntityExtractor()

    def commit_one_step_for_np_extraction(self, session, noun_phrase_list):
        session.commit()
        for (sentence, noun_phrase) in noun_phrase_list:
            relation = NounPhraseExtractFromSentenceRelation(np_id=noun_phrase.id, sentence_id=sentence.id)
            if relation.is_exist(session=session):
                continue
            else:
                relation.create(session=session, autocommit=False)
        session.commit()

    def start_extract_for_sentences(self, session, sentence_list, step):

        noun_phrase_list = []
        for sentence in sentence_list:
            chunk_strings = self.extractor.extract_chunks_strings(sentence.text)
            for chunk_string in chunk_strings:
                np = NounPhrase(text=chunk_string)
                np = np.find_or_create(session=session, autocommit=False)
                noun_phrase_list.append((sentence, np))

            if len(noun_phrase_list) > step:
                self.commit_one_step_for_np_extraction(session=session, noun_phrase_list=noun_phrase_list)
                noun_phrase_list = []
        self.commit_one_step_for_np_extraction(session=session, noun_phrase_list=noun_phrase_list)

    def start_extract_np_from_all_sentences(self):
        print("start extract np from all sentences")
        session = EngineFactory.create_session()
        sentence_text_list = DocumentSentenceText.get_all_valid_sentences(session)
        self.start_extract_for_sentences(session=session, sentence_list=sentence_text_list, step=5000)
        print("end extract np from all sentences")

    def commit_one_step_for_merge_np(self, clean_noun_phrase_with_id_list, session):
        session.commit()
        for (clean_noun_phrase, old_noun_phrase_id) in clean_noun_phrase_with_id_list:
            relation = NounPhraseMergeCleanFromNPRelation(new_np_id=clean_noun_phrase.id, old_np_id=old_noun_phrase_id)
            if relation.is_exist(session=session):
                continue
            else:
                relation.create(session=session, autocommit=False)
        session.commit()

    def merge_to_noun_phase_merge_clean(self, session, step):
        extractor = EntityExtractor()

        noun_phrase_list = session.query(NounPhrase).all()
        clean_noun_phrase_with_id_list = []
        print(len(noun_phrase_list))
        for n_p in noun_phrase_list:
            old_id = n_p.id
            old_text = n_p.text
            if old_text is not None and old_text != '':
                new_text = extractor.clean_np_text(old_text)
                if new_text != None:
                    np_clean = NounPhraseMergeClean(text=new_text)
                    np_clean_db = np_clean.find_or_create(session=session, autocommit=False)
                    clean_noun_phrase_with_id_list.append((np_clean_db, old_id))
                    if len(clean_noun_phrase_with_id_list) > step:
                        self.commit_one_step_for_merge_np(clean_noun_phrase_with_id_list, session=session)
                        clean_noun_phrase_with_id_list = []
        session.commit()

    def start_extract_merge_np(self):
        print("start extract merge np from np")
        session = EngineFactory.create_session()
        step = 3000
        self.merge_to_noun_phase_merge_clean(session, step)
        print("end extract merge np from np")

    def start_build_merge_np_from_sentence_relation(self):
        print("start build merge np from sentence relation")
        session = EngineFactory.create_session()
        all_merge_np_list = NounPhraseMergeClean.get_all_merge_np_list(session)
        count = 0
        step = 5000
        for merge_np in all_merge_np_list:
            merge_np_id = merge_np.id
            all_np_to_merge_np_relation_list = NounPhraseMergeCleanFromNPRelation.get_all_relation_by_merge_np_id(
                session=session, merge_np_id=merge_np.id)

            for np_to_merge_np_relation in all_np_to_merge_np_relation_list:
                np_id = np_to_merge_np_relation.old_np_id

                np_from_sentence_relation_list = NounPhraseExtractFromSentenceRelation.get_all_relation_by_np_id(
                    session=session, np_id=np_id)

                for np_from_sentence_relation in np_from_sentence_relation_list:

                    sentence_id = np_from_sentence_relation.sentence_id
                    relation = SentenceToMergeNPEntityRelation(sentence_id=sentence_id,
                                                               merge_np_id=merge_np_id)
                    print("create merge_np_id=%d to sentence_id=%d", merge_np_id, sentence_id)
                    relation.find_or_create(session=session, autocommit=False)
                    count = count + 1
                    if count > step:
                        count = 0
                        session.commit()
        session.commit()
        print("end build merge np from sentence relation")

    def clean_all_related_table(self, session):
        print("start delete relation")
        NounPhraseExtractFromDocumentRelation.delete_all(session)
        NounPhraseExtractFromSentenceRelation.delete_all(session)
        NounPhraseMergeCleanFromNPRelation.delete_all(session)
        SentenceToMergeNPEntityRelation.delete_all(session)
        print("end delete relation")
        print("start delete entity")
        NounPhraseMergeClean.delete_all(session)
        NounPhrase.delete_all(session)
        print("end delete entity")

    def start_extract_candidate_concept_entity_pipeline(self):
        # delete all table content first
        session = EngineFactory.create_session()
        self.clean_all_related_table(session)
        self.start_extract_np_from_all_sentences()
        self.start_extract_merge_np()
        self.start_build_merge_np_from_sentence_relation()
