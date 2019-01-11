import traceback
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, MetaData, ForeignKey, DateTime, Index, Boolean, func, Table, \
    SmallInteger, Float, or_
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from engine_factory import EngineFactory
from sqlalchemy_fulltext import FullText

Base = declarative_base()


class DomainEntity(Base):
    __tablename__ = 'java_documnet_domain_entity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), index=True)
    description = Column(LONGTEXT(), nullable=True)
    source_id = Column(Integer, index=True, nullable=True)  # one unique key to stand for the DomainEntity In AP cluster
    __table_args__ = (Index('domain_entity_unique_index', name, source_id),
                      {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, name=None, description=None, source_id=None):
        self.description = description
        self.name = name
        self.source_id = source_id

    @staticmethod
    def get_by_source_id(session, source_id):
        try:
            return session.query(DomainEntity).filter_by(source_id=source_id).first()
        except Exception:
            traceback.print_exc()
            return None

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(DomainEntity).filter(DomainEntity.source_id == self.source_id,
                                                          DomainEntity.name == func.binary(self.name.encode(
                                                              'utf-8'))).first()
            except Exception:
                traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    @staticmethod
    def get_all_domain_entity_id_and_name(session):

        try:
            return session.query(DomainEntity.id, DomainEntity.name).all()
        except Exception:
            traceback.print_exc()
            return []

    @staticmethod
    def get_all_domain_entities(session):
        try:
            return session.query(DomainEntity).all()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def delete_all(session):
        try:
            session.query(DomainEntity).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return

    @staticmethod
    def get_all_domain_entity_with_same_name(session, name):
        try:
            return session.query(DomainEntity).filter(DomainEntity.name == func.binary(name.encode(
                'utf-8'))).all()
        except Exception:
            traceback.print_exc()
            return []

    @staticmethod
    def get_all_domain_entity_name_distinct(session):
        try:
            return session.query(DomainEntity.name).distinct().all()
        except Exception:
            traceback.print_exc()
            return []


class DomainEntityExtractFromSentenceRelation(Base):
    __tablename__ = 'java_documnet_domain_entity_from_sentence_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(Integer, ForeignKey('java_api_document_sentence_text.id'), index=True, nullable=False)
    domain_entity_id = Column(Integer, ForeignKey('java_documnet_domain_entity.id'), index=True, nullable=False)
    __table_args__ = (Index('domain_entity_sentence_index', sentence_id, domain_entity_id),
                      {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, sentence_id, domain_entity_id):
        self.sentence_id = sentence_id
        self.domain_entity_id = domain_entity_id

    def is_exist(self, session):
        try:
            result = session.query(DomainEntityExtractFromSentenceRelation.id).filter(
                DomainEntityExtractFromSentenceRelation.sentence_id == self.sentence_id,
                DomainEntityExtractFromSentenceRelation.domain_entity_id == self.domain_entity_id).first()
            if result:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(DomainEntityExtractFromSentenceRelation).filter(
                    DomainEntityExtractFromSentenceRelation.sentence_id == self.sentence_id,
                    DomainEntityExtractFromSentenceRelation.domain_entity_id == self.domain_entity_id).first()

            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def get_all_relation_by_domain_entity_id(session, domain_entity_id):

        return session.query(DomainEntityExtractFromSentenceRelation).filter_by(
            domain_entity_id=domain_entity_id).all()

    @staticmethod
    def get_all_relation(session):

        return session.query(DomainEntityExtractFromSentenceRelation).all()

    @staticmethod
    def delete_all(session):
        try:
            session.query(DomainEntityExtractFromSentenceRelation).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return

    @staticmethod
    def get_max_id(session):
        return session.query(func.max(DomainEntityExtractFromSentenceRelation.id)).scalar()


class NounPhrase(Base):
    __tablename__ = 'java_documnet_noun_phase'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(512), index=True)

    def __init__(self, text):
        self.text = text

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(NounPhrase).filter(
                    NounPhrase.text == func.binary(self.text).encode('utf-8')).first()
            except Exception:
                traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    @staticmethod
    def delete_all(session):
        try:
            session.query(NounPhrase).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class AndroidAPIParameter(Base):
    __tablename__ = 'androidAPI_parameter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    parameter_text = Column(Text())
    method_id = Column(Integer)
    parameter_url = Column(String(512))
    type = Column(String(255))

    def __init__(self, name, parameter_text, method_id, parameter_url, type):
        self.name = name
        self.parameter_text = parameter_text
        self.method_id = method_id
        self.parameter_url = parameter_url
        self.type = type

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(AndroidAPIParameter).filter_by(name=self.name, parameter_text=self.parameter_text,
                                                                    method_id=self.method_id,
                                                                    parameter_url=self.parameter_url,
                                                                    type=self.type).first()
            except Exception:
                traceback.print_exc()
            return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance


class AndroidAPIReturnValue(Base):
    __tablename__ = 'androidAPI_return_value'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    return_value_text = Column(Text())
    method_id = Column(Integer)
    return_value_url = Column(String(512))
    type = Column(String(255))

    def __init__(self, name, return_value_text, method_id, return_value_url, type):
        self.name = name
        self.return_value_text = return_value_text
        self.method_id = method_id
        self.return_value_url = return_value_url
        self.type = type

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(AndroidAPIReturnValue).filter_by(name=self.name,
                                                                      return_value_text=self.return_value_text,
                                                                      method_id=self.method_id,
                                                                      return_value_url=self.return_value_url,
                                                                      type=self.type).first()
            except Exception:
                traceback.print_exc()
            return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance


class AndroidAPIThrow(Base):
    __tablename__ = 'androidAPI_throw'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    throw_text = Column(Text())
    method_id = Column(Integer)
    throw_url = Column(String(512))
    type = Column(String(255))

    def __init__(self, name, throw_text, method_id, throw_url, type):
        self.name = name
        self.throw_text = throw_text
        self.method_id = method_id
        self.throw_url = throw_url
        self.type = type

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(AndroidAPIThrow).filter_by(name=self.name, throw_text=self.throw_text,
                                                                method_id=self.method_id, throw_url=self.throw_url,
                                                                type=self.type).first()
            except Exception:
                traceback.print_exc()
            return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance


class NounPhraseMergeClean(Base):
    __tablename__ = 'java_documnet_noun_phase_merge_clean'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(512), index=True)

    def __init__(self, text):
        self.text = text

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(NounPhraseMergeClean).filter(
                    NounPhraseMergeClean.text == func.binary(self.text)).first()
            except Exception:
                traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    @staticmethod
    def get_all_merge_np_list(session):
        return session.query(NounPhraseMergeClean).all()

    @staticmethod
    def delete_all(session):
        try:
            session.query(NounPhraseMergeClean).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class NounPhraseMergeCleanFromNPRelation(Base):
    __tablename__ = 'java_documnet_noun_phase_merge_clean_from_np_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    new_np_id = Column(Integer, ForeignKey('java_documnet_noun_phase_merge_clean.id'), index=True, nullable=False)
    old_np_id = Column(Integer, ForeignKey('java_documnet_noun_phase.id'), index=True, nullable=False)

    def __init__(self, new_np_id, old_np_id):
        self.new_np_id = new_np_id
        self.old_np_id = old_np_id

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(NounPhraseMergeCleanFromNPRelation).filter(
                    NounPhraseMergeCleanFromNPRelation.new_np_id == func.binary(
                        self.new_np_id), NounPhraseMergeCleanFromNPRelation.old_np_id == func.binary(
                        self.old_np_id)).first()
            except Exception:
                traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def is_exist(self, session):
        try:
            result = session.query(NounPhraseMergeCleanFromNPRelation.id).filter(
                NounPhraseMergeCleanFromNPRelation.old_np_id == self.old_np_id,
                NounPhraseMergeCleanFromNPRelation.new_np_id == self.new_np_id).first()
            if result:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    @staticmethod
    def get_all_relation_by_merge_np_id(session, merge_np_id):
        return session.query(NounPhraseMergeCleanFromNPRelation).filter(
            NounPhraseMergeCleanFromNPRelation.new_np_id == merge_np_id).all()

    @staticmethod
    def delete_all(session):
        try:
            session.query(NounPhraseMergeCleanFromNPRelation).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class AndroidAPIMethod(Base):
    __tablename__ = 'androidAPI_method'
    id = Column(Integer, primary_key=True, autoincrement=True)
    method_name = Column(String(255))
    short_description_label = Column(Text())
    short_description = Column(Text())
    long_description_label = Column(LONGTEXT())
    long_description_remove_table_label = Column(LONGTEXT())
    long_description = Column(LONGTEXT())
    return_value = Column(String(255))
    type = Column(String(255))
    add_in_level = Column(Integer)
    full_declaration = Column(Text())
    class_id = Column(Integer)

    def __init__(self, method_name, short_description_label, short_description, long_description_label,
                 long_description_remove_table_label,
                 long_description, return_value, type, add_in_level, full_declaration, class_id):
        self.method_name = method_name
        self.short_description_label = short_description_label
        self.short_description = short_description
        self.long_description_label = long_description_label
        self.long_description_remove_table_label = long_description_remove_table_label
        self.long_description = long_description
        self.return_value = return_value
        self.type = type
        self.add_in_level = add_in_level
        self.full_declaration = full_declaration
        self.class_id = class_id

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(AndroidAPIMethod.id).filter(
                    AndroidAPIMethod.method_name == self.method_name,
                    AndroidAPIMethod.class_id == self.class_id).first()
            except Exception:
                traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self


class NounPhraseExtractFromDocumentRelation(Base):
    __tablename__ = 'java_documnet_noun_phase_from_doc_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey('java_api_document_text.id'), index=True, nullable=False)
    np_id = Column(Integer, ForeignKey('java_documnet_noun_phase.id'), index=True, nullable=False)
    __table_args__ = (Index('np_doc_index', doc_id, np_id),
                      {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, doc_id, np_id):
        self.doc_id = doc_id
        self.np_id = np_id

    def is_exist(self, session):
        try:
            result = session.query(NounPhraseExtractFromDocumentRelation.id).filter(
                NounPhraseExtractFromDocumentRelation.doc_id == self.doc_id,
                NounPhraseExtractFromDocumentRelation.np_id == self.np_id).first()
            if result:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(NounPhraseExtractFromDocumentRelation.id).filter(
                    NounPhraseExtractFromDocumentRelation.doc_id == self.doc_id,
                    NounPhraseExtractFromDocumentRelation.np_id == self.np_id).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def delete_all(session):
        try:
            session.query(NounPhraseExtractFromDocumentRelation).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class NounPhraseExtractFromSentenceRelation(Base):
    __tablename__ = 'java_documnet_noun_phase_from_sentence_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(Integer, ForeignKey('java_api_document_sentence_text.id'), index=True, nullable=False)
    np_id = Column(Integer, ForeignKey('java_documnet_noun_phase.id'), index=True, nullable=False)
    __table_args__ = (Index('np_sentence_index', sentence_id, np_id),
                      {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, sentence_id, np_id):
        self.sentence_id = sentence_id
        self.np_id = np_id

    def is_exist(self, session):
        try:
            result = session.query(NounPhraseExtractFromSentenceRelation.id).filter(
                NounPhraseExtractFromSentenceRelation.sentence_id == self.sentence_id,
                NounPhraseExtractFromSentenceRelation.np_id == self.np_id).first()
            if result:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(NounPhraseExtractFromSentenceRelation.id).filter(
                    NounPhraseExtractFromSentenceRelation.sentence_id == self.sentence_id,
                    NounPhraseExtractFromSentenceRelation.np_id == self.np_id).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def get_all_relation_by_np_id(session, np_id):

        return session.query(NounPhraseExtractFromSentenceRelation).filter_by(
            np_id=np_id).all()

    @staticmethod
    def delete_all(session):
        try:
            session.query(NounPhraseExtractFromSentenceRelation).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)  # auto incrementing
    logger = Column(String(256))  # the name of the logger.
    level = Column(String(50))  # info, debug, or error?
    trace = Column(LONGTEXT())  # the full traceback printout
    msg = Column(LONGTEXT())  # any custom log you may have included
    path = Column(String(64))
    ip = Column(String(32))
    method = Column(String(64))
    created_at = Column(DateTime, default=func.now())  # the current timestamp

    def __init__(self, logger=None, level=None, trace=None, msg=None, path=None, ip=None, method=None):
        self.logger = logger
        self.level = level
        self.trace = trace
        self.msg = msg
        self.path = path
        self.ip = ip
        self.method = method

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Log: %s - %s>" % (self.created_at.strftime('%m/%d/%Y-%H:%M:%S'), self.msg[:50])


class WikipediaEntityName(Base, FullText):
    __tablename__ = 'wikipedia_entity_name'
    __fulltext_columns__ = ('name',)
    id = Column(Integer, primary_key=True, autoincrement=True)
    kg_id = Column(Integer, index=True, nullable=False)
    name = Column(String(256), index=True, nullable=False)

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, kg_id, name):
        self.kg_id = kg_id
        self.name = name

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                try:
                    session.commit()
                except:
                    session.rollback()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(WikipediaEntityName).filter_by(kg_id=self.kg_id, name=self.name).first()
            except Exception:
                traceback.print_exc()
                session.rollback()
                return None

    @staticmethod
    def get_candidate_by_word(session, word):
        try:
            query_str = "%" + str(word) + "%"
            return session.query(WikipediaEntityName).filter(WikipediaEntityName.name.like(query_str)).all()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_all_wikipedia_names(session):
        try:
            return session.query(WikipediaEntityName).all()
        except Exception:
            traceback.print_exc()
            return []

    @staticmethod
    def delete_all(session):
        try:
            session.query(WikipediaEntityName).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return

    def __repr__(self):
        return '<WikipediaEntityName: id=%r kg_id=%r name=%r>' % (self.id, self.kg_id, self.name)


class WikipediaEntityNameToWikipediaMapping(Base):
    __tablename__ = 'wikipedia_entity_name_wikipedia_maping'
    id = Column(Integer, primary_key=True, autoincrement=True)
    kg_id = Column(Integer, index=True, nullable=False)
    wiki_pedia_id = Column(Integer, index=True, nullable=False)

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, kg_id, wiki_pedia_id):
        self.kg_id = kg_id
        self.wiki_pedia_id = wiki_pedia_id

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(WikipediaEntityNameToWikipediaMapping).filter_by(kg_id=self.kg_id,
                                                                                      wiki_pedia_id=self.wiki_pedia_id).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def get_wikipedia_id_by_kg_id(session, kg_id):
        try:
            return session.query(WikipediaEntityNameToWikipediaMapping.wiki_pedia_id).filter_by(kg_id=kg_id).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_kg_id_by_wikipedia_id(session, wikipedia_id):
        try:
            return session.query(WikipediaEntityNameToWikipediaMapping.kg_id).filter_by(
                wikipedia_id=wikipedia_id).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def delete_all(session):
        try:
            session.query(WikipediaEntityNameToWikipediaMapping).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class WikiDataProperty(Base):
    __tablename__ = 'wikidata_property'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wd_item_id = Column(String(256), nullable=False, unique=True)
    property_name = Column(String(512), nullable=False)
    data_json = Column(LONGTEXT())

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, wd_item_id, property_name, data_json):
        self.wd_item_id = wd_item_id
        self.property_name = property_name
        self.data_json = data_json

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(WikiDataProperty).filter(WikiDataProperty.wd_item_id == self.wd_item_id).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def get_property_by_wd_item_id(session, wd_item_id):
        try:
            property_object = session.query(WikiDataProperty).filter(WikiDataProperty.wd_item_id == wd_item_id).first()
            return property_object
        except Exception:
            traceback.print_exc()
            return None


class WikiDataItem(Base):
    __tablename__ = 'wikidata_item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wd_item_id = Column(String(32), nullable=False, unique=True)
    wd_item_name = Column(String(256), nullable=False, index=True)
    data_json = Column(LONGTEXT())

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, wd_item_id, wd_item_name, data_json):
        self.wd_item_id = wd_item_id
        self.wd_item_name = wd_item_name
        self.data_json = data_json

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(WikiDataItem).filter(WikiDataItem.wd_item_id == self.wd_item_id).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def get_wd_item_by_wd_item_id(session, wd_item_id):
        try:
            property_object = session.query(WikiDataItem).filter(WikiDataItem.wd_item_id == wd_item_id).first()
            return property_object
        except Exception:
            traceback.print_exc()
            return None


class WikidataAnnotation(Base):
    __tablename__ = 'wikidata_annotation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wd_item_id = Column(String(32), nullable=True, index=True)
    type = Column(Integer, index=True)
    url = Column(String(256), index=True, nullable=True)
    name = Column(String(256), index=True, nullable=True)
    description = Column(String(1024), index=True, nullable=True)

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, wd_item_id, type, description, url, name):
        self.wd_item_id = wd_item_id
        self.type = type
        self.description = description
        self.url = url
        self.name = name

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                result = session.query(WikidataAnnotation).filter(
                    WikidataAnnotation.wd_item_id == self.wd_item_id).first()
                return result
            except Exception:
                traceback.print_exc()
                return None


class WikipediaDocument(Base):
    __tablename__ = 'wiki_pedia'
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, autoincrement=True)
    url = Column(String(256), index=True, nullable=False)
    title = Column(String(128), index=True, nullable=False)
    content = Column(LONGTEXT())

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, doc_id, url, content):
        self.doc_id = doc_id
        self.url = url
        self.content = content

    @staticmethod
    def get_document_by_wikipedia_title(session, title):
        try:
            return session.query(WikipediaDocument).filter_by(title=func.binary(title)).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_candidate_by_word(session, word):
        try:
            query_str = "%" + str(word) + "%"
            return session.query(WikipediaDocument).filter(WikipediaDocument.title.like(query_str)).all()
        except Exception:
            traceback.print_exc()
            return None


class ClassifiedWikipediaDocumentLR(Base):
    TYPE_SOFTWARE_RELATED = 1
    TYPE_SOFTWARE_UNRELATED = 0

    __tablename__ = 'classified_wiki_doc_lr_v2'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), index=True, nullable=True)
    url = Column(String(256), index=True, nullable=False)
    content = Column(LONGTEXT(), nullable=True)
    type = Column(Integer, index=True, nullable=False)
    score = Column(Float, index=True, nullable=False)
    # wikipedia_doc_id = Column(Integer, ForeignKey('wiki_pedia.id'), nullable=False)
    wikipedia_doc_id = Column(Integer, nullable=False, index=True)

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, title, url, type, score, wikipedia_doc_id):
        self.title = title
        self.url = url
        self.type = type
        self.score = score
        self.wikipedia_doc_id = wikipedia_doc_id

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def create(self, session):
        session.add(self)

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(ClassifiedWikipediaDocumentLR).filter(
                    ClassifiedWikipediaDocumentLR.wikipedia_doc_id == self.wikipedia_doc_id).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def get_classified_doc(session, wikipedia_doc_id):
        try:
            instance = session.query(ClassifiedWikipediaDocumentLR).filter(
                ClassifiedWikipediaDocumentLR.wikipedia_doc_id == wikipedia_doc_id).first()
            return instance
        except Exception:
            traceback.print_exc()
            return None

    def __repr__(self):
        return '<ClassifiedWikipediaDocumentLR: title=%r score=%r>' % (self.title, self.score)

    @staticmethod
    def delete_all(session):
        try:
            session.query(ClassifiedWikipediaDocumentLR).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class WikipediaAnnotation(Base):
    __tablename__ = 'wikipedia_annotation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wd_item_id = Column(String(32), nullable=True, index=True)
    wd_item_name = Column(String(256), nullable=True, index=True)
    wikipedia_url = Column(String(256), nullable=True, index=True)
    wikipedia_title = Column(String(128), nullable=True, index=True)
    wikipedia_text = Column(LONGTEXT(), nullable=True)
    data_json = Column(LONGTEXT(), nullable=True)

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, wd_item_id, wd_item_name, wikipedia_url, wikipedia_title, wikipedia_text, data_json):
        self.wd_item_id = wd_item_id
        self.wd_item_name = wd_item_name
        self.data_json = data_json
        self.wikipedia_url = wikipedia_url
        self.wikipedia_title = wikipedia_title
        self.wikipedia_text = wikipedia_text

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                if self.wd_item_id:
                    result = session.query(WikidataAndWikipediaData).filter(
                        WikidataAndWikipediaData.wd_item_id == self.wd_item_id).first()
                    if result:
                        return result
                if self.wikipedia_url:
                    result = session.query(WikidataAndWikipediaData).filter(
                        WikidataAndWikipediaData.wikipedia_url == self.wikipedia_url).first()

                    return result
            except Exception:
                traceback.print_exc()
                return None


class WikidataAndWikipediaData(Base):
    __tablename__ = 'wikidata_wikipedia_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wd_item_id = Column(String(32), nullable=True, index=True)
    wd_item_name = Column(String(256), nullable=True, index=True)
    wikipedia_url = Column(String(256), nullable=True, index=True)
    wikipedia_title = Column(String(128), nullable=True, index=True)
    wikipedia_text = Column(LONGTEXT(), nullable=True)
    data_json = Column(LONGTEXT(), nullable=True)

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, wd_item_id, wd_item_name, wikipedia_url, wikipedia_title, wikipedia_text, data_json):
        self.wd_item_id = wd_item_id
        self.wd_item_name = wd_item_name
        self.data_json = data_json
        self.wikipedia_url = wikipedia_url
        self.wikipedia_title = wikipedia_title
        self.wikipedia_text = wikipedia_text

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    @staticmethod
    def is_exist_wikidata_json(session, wd_item_id):

        try:
            if wd_item_id:
                result = session.query(WikidataAndWikipediaData).filter(
                    WikidataAndWikipediaData.wd_item_id == wd_item_id).first()
                if result:
                    return True
            return False
        except Exception:
            traceback.print_exc()
            return False

    @staticmethod
    def is_exist_wikipedia_url(session, wikipeida_url):

        try:
            if wikipeida_url:
                result = session.query(WikidataAndWikipediaData).filter(
                    WikidataAndWikipediaData.wikipedia_url == wikipeida_url).first()
                if result:
                    return True
            return False
        except Exception:
            traceback.print_exc()
            return False

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                if self.wd_item_id:
                    result = session.query(WikidataAndWikipediaData).filter(
                        WikidataAndWikipediaData.wd_item_id == self.wd_item_id).first()
                    if result:
                        return result
                if self.wikipedia_url:
                    result = session.query(WikidataAndWikipediaData).filter(
                        WikidataAndWikipediaData.wikipedia_url == self.wikipedia_url).first()

                    return result
            except Exception:
                traceback.print_exc()
                return None


class EntityHeat(Base):
    __tablename__ = 'api_heat'
    id = Column(Integer, primary_key=True, autoincrement=True)
    heat = Column(Integer, index=True)
    api_id = Column(Integer, nullable=False, index=True)

    def __init__(self, heat, api_id):
        self.heat = heat
        self.api_id = api_id

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return '<APIHeat: %r: api_id=%s >' % (self.heat, self.api_id)


class APIRelation(Base):
    RELATION_TYPE_BELONG_TO = 1
    RELATION_TYPE_EXTENDS = 2
    RELATION_TYPE_IMPLEMENTS = 3
    RELATION_TYPE_SEE_ALSO = 4
    RELATION_TYPE_THROW_EXCEPTION = 5
    RELATION_TYPE_RETURN_VALUE = 6
    RELATION_TYPE_HAS_PARAMETER = 7
    RELATION_TYPE_HAS_RETURN_VALUE = 8
    RELATION_TYPE_HAS_EXCEPTION = 9
    RELATION_TYPE_PARAMETER_HAS_TYPE = 10
    RELATION_TYPE_RETURN_VALUE_HAS_TYPE = 11
    RELATION_TYPE_EXCEPTION_HAS_TYPE = 12

    __tablename__ = 'java_api_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_api_id = Column(Integer, ForeignKey('java_all_api_entity.id'), nullable=False, index=True)
    end_api_id = Column(Integer, ForeignKey('java_all_api_entity.id'), nullable=False, index=True)
    relation_type = Column(Integer, index=True)

    __table_args__ = (Index('unique_index', start_api_id, end_api_id, relation_type),
                      Index('all_relation_index', start_api_id, end_api_id),
                      {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, start_api_id, end_api_id, relation_type):
        self.start_api_id = start_api_id
        self.end_api_id = end_api_id
        self.relation_type = relation_type

    def exist_in_remote(self, session):
        try:
            if session.query(APIRelation.id).filter_by(start_api_id=self.start_api_id,
                                                       end_api_id=self.end_api_id,
                                                       relation_type=self.relation_type).first():
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIRelation).filter_by(start_api_id=self.start_api_id,
                                                            end_api_id=self.end_api_id,
                                                            relation_type=self.relation_type).first()
            except Exception:
                # traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def __repr__(self):
        return '<APIRelation: %r-%r: type=%r >' % (self.start_api_id, self.end_api_id, self.relation_type)

    @staticmethod
    def get_api_relation_by_start_and_end_api_id(session, start_api_id, end_api_id):
        try:
            api_relation = session.query(APIRelation).filter_by(start_api_id=start_api_id,
                                                                end_api_id=end_api_id).first()
            return api_relation
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_type_string(relation_type):
        if relation_type == APIRelation.RELATION_TYPE_BELONG_TO:
            return "belong to"
        if relation_type == APIRelation.RELATION_TYPE_EXTENDS:
            return "extend"
        if relation_type == APIRelation.RELATION_TYPE_IMPLEMENTS:
            return "implement"
        if relation_type == APIRelation.RELATION_TYPE_SEE_ALSO:
            return "see also"
        if relation_type == APIRelation.RELATION_TYPE_THROW_EXCEPTION:
            return "throw exception"
        if relation_type == APIRelation.RELATION_TYPE_RETURN_VALUE:
            return "return value type"

        if relation_type == APIRelation.RELATION_TYPE_HAS_PARAMETER:
            return "has parameter"
        if relation_type == APIRelation.RELATION_TYPE_HAS_RETURN_VALUE:
            return "has return value"
        if relation_type == APIRelation.RELATION_TYPE_HAS_EXCEPTION:
            return "has exception"

        if relation_type == APIRelation.RELATION_TYPE_PARAMETER_HAS_TYPE:
            return "has type"
        if relation_type == APIRelation.RELATION_TYPE_RETURN_VALUE_HAS_TYPE:
            return "has type"
        if relation_type == APIRelation.RELATION_TYPE_EXCEPTION_HAS_TYPE:
            return "has type"

        return ""


has_alias_table = Table('has_alias', Base.metadata,
                        Column('api_id', Integer, ForeignKey('java_all_api_entity.id')),
                        Column('alias_id', Integer, ForeignKey('java_api_alias.id'))
                        )


class APIAlias(Base, FullText):
    __tablename__ = 'java_api_alias'
    __fulltext_columns__ = ('alias',)

    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String(1024), nullable=False, index=True)
    type = Column(Integer, nullable=True, index=True)

    all_apis = relationship(
        "APIEntity",
        secondary=has_alias_table,
        back_populates="all_aliases")

    ALIAS_TYPE_QUALIFIER_NAME = 1

    # all api only with simple name, for example android.view.Button -> Button
    ALIAS_TYPE_SIMPLE_NAME = 2
    # all api only with api type + simple name, for example android.view.Button -> class Button
    ALIAS_TYPE_SIMPLE_NAME_WITH_TYPE = 3
    # only for method. qualifier type. etc. append(java.lang.Object)
    ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE = 4
    ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE = 5
    ALIAS_TYPE_SIMPLE_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE = 6
    ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE = 7

    # for field and other,javax.xml.transform.OutputKeys.DOCTYPE_SYSTEM->OutputKeys.DOCTYPE_SYSTEM, save the last two
    ALIAS_TYPE_SIMPLE_PARENT_API_NAME_WITH_SIMPLE_NAME = 8
    # @nullable
    ALIAS_TYPE_ANNOTATION_REFERENCE = 9

    ALIAS_TYPE_CAMEL_CASE_TO_SPACE = 10
    ALIAS_TYPE_UNDERLINE_TO_SPACE = 11
    ALIAS_TYPE_VALUE_ALIAS = 12  # for parameter and return value and exception

    __table_args__ = (Index('alias_type_index', alias, type), {
        "mysql_charset": "utf8",
    })

    def __init__(self, alias, type):
        self.alias = alias
        self.type = type

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIAlias).filter(APIAlias.alias == func.binary(self.alias),
                                                      APIAlias.type == self.type,
                                                      ).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def aliases_to_apis(aliases):
        api_entity_set = set()

        for alias in aliases:
            for api in alias.all_apis:
                api_entity_set.add(api)
        return api_entity_set

    def __eq__(self, other):
        if isinstance(other, APIAlias):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<APIAlias: id=%r alias=%r type=%r >' % (self.id, self.alias, self.type)

    @staticmethod
    def delete_all(session):
        try:
            session.query(has_alias_table).delete()
            session.query(APIAlias).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class APIDocumentWebsite(Base):
    __tablename__ = 'java_api_document_website'
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey('java_all_api_entity.id'), nullable=False)
    document_website = Column(String(512), nullable=False)
    __table_args__ = (Index('api_document_website_index', api_id, document_website), {
        "mysql_charset": "utf8",
    })

    def __init__(self, api_id, document_website):
        self.api_id = api_id
        self.document_website = document_website

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIDocumentWebsite).filter(APIDocumentWebsite.api_id == self.api_id,
                                                                APIDocumentWebsite.document_website == func.binary(
                                                                    self.document_website)).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def get_api_id_by_website(session, website):
        try:
            api_id = session.query(APIDocumentWebsite.api_id).filter_by(document_website=website).scalar()
            return api_id
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_document_website_list_by_api_id(session, api_id):
        try:
            document_website_list = session.query(APIDocumentWebsite.document_website).filter_by(api_id=api_id).all()
            return document_website_list
        except Exception:
            traceback.print_exc()
            return None


class APIEntity(Base):
    API_TYPE_ALL_API_ENTITY = -1

    API_TYPE_UNKNOWN = 0
    API_TYPE_PACKAGE = 1
    API_TYPE_CLASS = 2
    API_TYPE_INTERFACE = 3
    API_TYPE_EXCEPTION = 4
    API_TYPE_ERROR = 5
    API_TYPE_FIELD = 6
    API_TYPE_CONSTRUCTOR = 7
    API_TYPE_ENUM_CLASS = 8
    API_TYPE_ANNOTATION = 9
    API_TYPE_XML_ATTRIBUTE = 10
    API_TYPE_METHOD = 11
    API_TYPE_ENUM_CONSTANTS = 12
    API_TYPE_PRIMARY_TYPE = 13
    API_TYPE_PARAMETER = 14
    API_TYPE_RETURN_VALUE = 15
    API_TYPE_EXCEPTION_CONDITION = 16
    __tablename__ = 'java_all_api_entity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_type = Column(Integer, default=API_TYPE_UNKNOWN, index=True)
    qualified_name = Column(String(1024), index=True)
    full_declaration = Column(String(1024), nullable=True, index=True)
    short_description = Column(Text(), nullable=True)
    added_in_version = Column(String(128), nullable=True)
    document_websites = relationship("APIDocumentWebsite", foreign_keys=[APIDocumentWebsite.api_id], backref="api")

    out_relation = relationship('APIRelation', foreign_keys=[APIRelation.start_api_id],
                                backref='start_api')
    in_relation = relationship('APIRelation', foreign_keys=[APIRelation.end_api_id],
                               backref='end_api')

    all_aliases = relationship(
        "APIAlias",
        secondary=has_alias_table,
        back_populates="all_apis")

    __table_args__ = {
        "mysql_charset": "utf8"
    }

    def __init__(self, qualified_name, api_type, full_declaration=None, short_description=None, added_in_version=None):
        self.api_type = api_type
        self.qualified_name = qualified_name
        self.full_declaration = full_declaration
        self.short_description = short_description
        self.added_in_version = added_in_version

    def find_or_create(self, session, autocommit=True):
        if self.api_type == APIEntity.API_TYPE_PARAMETER or self.api_type == APIEntity.API_TYPE_RETURN_VALUE or self.api_type == APIEntity.API_TYPE_EXCEPTION_CONDITION:
            remote_instance = self.get_remote_parameter_object(session)
        else:
            remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIEntity).filter(
                    APIEntity.qualified_name == func.binary(self.qualified_name)).first()
            except Exception:
                traceback.print_exc()
                return None

    def get_remote_parameter_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIEntity).filter_by(qualified_name=self.qualified_name,
                                                          full_declaration=self.full_declaration,
                                                          short_description=self.short_description).first()
            except Exception:
                traceback.print_exc()
                return None

    @staticmethod
    def exist(session, qualified_name):
        try:
            if session.query(APIEntity.id).filter(APIEntity.qualified_name == func.binary(qualified_name)).first():
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def find_by_id(session, api_entity_id):
        try:
            return session.query(APIEntity).filter(APIEntity.id == api_entity_id).first()
        except Exception:
            return None

    @staticmethod
    def find_by_qualifier(session, qualified_name):
        try:
            return session.query(APIEntity).filter(APIEntity.qualified_name == func.binary(qualified_name)).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def find_by_full_declaration_and_description(session, full_declaration, description):
        try:
            return session.query(APIEntity).filter_by(full_declaration=func.binary(full_declaration),
                                                      short_description=description).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_api_type_string(type):
        if type == APIEntity.API_TYPE_UNKNOWN:
            return []
        if type == APIEntity.API_TYPE_PACKAGE:
            return ["package"]
        if type == APIEntity.API_TYPE_CLASS:
            return ["class"]
        if type == APIEntity.API_TYPE_INTERFACE:
            return ["interface", "class"]
        if type == APIEntity.API_TYPE_EXCEPTION:
            return ["exception", "class"]
        if type == APIEntity.API_TYPE_ERROR:
            return ["error", "class"]
        if type == APIEntity.API_TYPE_FIELD:
            return ["field", "constant"]
        if type == APIEntity.API_TYPE_CONSTRUCTOR:
            return ["constructor", "constructor method"]
        if type == APIEntity.API_TYPE_ENUM_CLASS:
            return ["enum", "constant", "enum class"]
        if type == APIEntity.API_TYPE_ANNOTATION:
            return ["annotation"]
        if type == APIEntity.API_TYPE_XML_ATTRIBUTE:
            return ["XML attribute", "attribute"]
        if type == APIEntity.API_TYPE_METHOD:
            return ["API", "method"]

        if type == APIEntity.API_TYPE_ENUM_CONSTANTS:
            return ["constant", "enum constant"]
        return []

    @staticmethod
    def get_simple_type_string(type):
        if type == APIEntity.API_TYPE_UNKNOWN:
            return ""
        if type == APIEntity.API_TYPE_PACKAGE:
            return "api package"
        if type == APIEntity.API_TYPE_CLASS:
            return "api class"
        if type == APIEntity.API_TYPE_INTERFACE:
            return "api interface"
        if type == APIEntity.API_TYPE_EXCEPTION:
            return "api exception"
        if type == APIEntity.API_TYPE_ERROR:
            return "api error"
        if type == APIEntity.API_TYPE_FIELD:
            return "api field"
        if type == APIEntity.API_TYPE_CONSTRUCTOR:
            return "api constructor"
        if type == APIEntity.API_TYPE_ENUM_CLASS:
            return "api enum class"
        if type == APIEntity.API_TYPE_ANNOTATION:
            return "api annotation"
        if type == APIEntity.API_TYPE_XML_ATTRIBUTE:
            return "api xml attribute"
        if type == APIEntity.API_TYPE_METHOD:
            return "api method"
        if type == APIEntity.API_TYPE_ENUM_CONSTANTS:
            return "api enum constant"

        if type == APIEntity.API_TYPE_PARAMETER:
            return "api parameter"
        if type == APIEntity.API_TYPE_RETURN_VALUE:
            return "api return value"
        if type == APIEntity.API_TYPE_EXCEPTION_CONDITION:
            return "api exception"
        return ""

    def __repr__(self):
        return '<APIEntity: id=%r name=%r>' % (self.id, self.qualified_name)

    def __eq__(self, other):
        if isinstance(other, APIEntity):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        return hash(self.id)

    @staticmethod
    def type_string_to_api_type_constant(api_type_string):
        if not api_type_string:
            return APIEntity.API_TYPE_UNKNOWN
        api_type_string = api_type_string.strip()
        if not api_type_string:
            return APIEntity.API_TYPE_UNKNOWN
        api_type_string = api_type_string.lower()
        if api_type_string == "package":
            return APIEntity.API_TYPE_PACKAGE
        if api_type_string == "class":
            return APIEntity.API_TYPE_CLASS
        if api_type_string == "interface":
            return APIEntity.API_TYPE_INTERFACE
        if api_type_string == "error":
            return APIEntity.API_TYPE_ERROR
        if api_type_string == "enum":
            return APIEntity.API_TYPE_ENUM_CLASS
        if api_type_string == "exception":
            return APIEntity.API_TYPE_EXCEPTION
        if api_type_string == "annotation type" or api_type_string == "annotation":
            return APIEntity.API_TYPE_ANNOTATION

        if api_type_string == "method":
            return APIEntity.API_TYPE_METHOD
        if api_type_string == "constructor":
            return APIEntity.API_TYPE_CONSTRUCTOR
        if api_type_string == "nested" or api_type_string == "nested class":
            return APIEntity.API_TYPE_CLASS
        if api_type_string == "required":
            return APIEntity.API_TYPE_FIELD
        if api_type_string == "optional":
            return APIEntity.API_TYPE_FIELD
        if api_type_string == "field":
            return APIEntity.API_TYPE_FIELD
        if api_type_string == "enum constant":
            return APIEntity.API_TYPE_ENUM_CONSTANTS

        return APIEntity.API_TYPE_UNKNOWN

    @staticmethod
    def api_type_belong_to_relation(api_type, subject_api_type):
        if api_type == subject_api_type:
            return True
        if subject_api_type == APIEntity.API_TYPE_METHOD:
            if api_type == APIEntity.API_TYPE_CONSTRUCTOR:
                return True

        if subject_api_type == APIEntity.API_TYPE_CLASS:
            if api_type == APIEntity.API_TYPE_INTERFACE:
                return True
            if api_type == APIEntity.API_TYPE_ERROR:
                return True
            if api_type == APIEntity.API_TYPE_ENUM_CLASS:
                return True
            if api_type == APIEntity.API_TYPE_EXCEPTION:
                return True
        if subject_api_type == APIEntity.API_TYPE_FIELD:

            if api_type == APIEntity.API_TYPE_ENUM_CONSTANTS:
                return True

        return False

    @staticmethod
    def get_api_id_list(session):
        try:
            return session.query(APIEntity.id).all()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_api_id_and_qualified_name_list(session):
        try:
            return session.query(APIEntity.id,APIEntity.qualified_name).all()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_all_API_entity(session):
        try:
            return session.query(APIEntity).all()
        except Exception:
            traceback.print_exc()
            return []

    @staticmethod
    def get_all_value_instance_api(session):
        try:
            return session.query(APIEntity).filter(or_(APIEntity.api_type == APIEntity.API_TYPE_EXCEPTION_CONDITION,
                                                       APIEntity.api_type == APIEntity.API_TYPE_PARAMETER,
                                                       APIEntity.api_type == APIEntity.API_TYPE_RETURN_VALUE)).all()
        except Exception:
            traceback.print_exc()
            return []


class APIEntityProperty(Base):
    __tablename__ = 'java_api_property'
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey('java_all_api_entity.id'), nullable=False, index=True)
    property_name = Column(String(512), nullable=False, index=True)
    property_value = Column(LONGTEXT(), nullable=True)  # text with no html tags

    __table_args__ = (Index('api_id_property_name_index', api_id, property_name, unique=True), {
        "mysql_charset": "utf8",
    })

    def __init__(self, api_id, property_name, property_value):
        self.api_id = api_id
        self.property_name = property_name
        self.property_value = property_value

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self


class APIHTMLText(Base):
    __tablename__ = 'java_api_html_text'
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey('java_all_api_entity.id'), nullable=False)
    html = Column(LONGTEXT(), nullable=False)
    clean_text = Column(LONGTEXT(), nullable=True)  # text with no html tags
    reserve_part_tag_text = Column(LONGTEXT(), nullable=True)  # text with only code tags text
    html_type = Column(Integer, nullable=True)

    __table_args__ = (Index('api_id_text_type_index', api_id, html_type), {
        "mysql_charset": "utf8",
    })

    HTML_TYPE_UNKNOWN = 0
    HTML_TYPE_API_DECLARATION = 1
    HTML_TYPE_API_SHORT_DESCRIPTION = 2
    HTML_TYPE_API_DETAIL_DESCRIPTION = 3
    HTML_TYPE_METHOD_RETURN_VALUE_DESCRIPTION = 4

    def __init__(self, api_id, html, html_type=HTML_TYPE_UNKNOWN):
        self.api_id = api_id
        self.html = html
        self.html_type = html_type

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    @staticmethod
    def get_by_id(session, id):
        try:
            return session.query(APIHTMLText).filter_by(id=id).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_text_by_api_id_and_type(session, api_id, html_type):
        try:
            return session.query(APIHTMLText.clean_text).filter_by(api_id=api_id, html_type=html_type).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_remote_object(session, api_id, html_type):
        try:
            return session.query(APIHTMLText).filter_by(api_id=api_id, html_type=html_type).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_html_text_id(session, api_id, html_type):
        try:
            return session.query(APIHTMLText.id).filter_by(api_id=api_id, html_type=html_type).first()
        except Exception:
            traceback.print_exc()
            return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session, api_id=self.api_id, html_type=self.html_type)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance


class DocumentSourceRecord(Base):
    __tablename__ = 'java_document_source_record'
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey('java_api_document_text.id'), unique=True, nullable=False)
    kg_table_id = Column(Integer, nullable=False)
    kg_table_primary_key = Column(Integer, nullable=False)

    __table_args__ = (Index('source_table_index', kg_table_id, kg_table_primary_key), {
        "mysql_charset": "utf8",
    })

    def __init__(self, doc_id, kg_table_id, kg_table_primary_key):
        self.doc_id = doc_id
        self.kg_table_id = kg_table_id
        self.kg_table_primary_key = kg_table_primary_key

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    @staticmethod
    def exist_import_record(session, kg_table_id, kg_table_primary_key):
        """
        check if the start_row_id has map in end_knowledge_table

        """

        try:
            team = session.query(DocumentSourceRecord).filter_by(kg_table_id=kg_table_id,
                                                                 kg_table_primary_key=kg_table_primary_key).first()
            if team:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False


class DocumentText(Base):
    __tablename__ = 'java_api_document_text'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # todo ,remove the html_text_id, it is not neccessary,because the doc source table
    html_text_id = Column(Integer, ForeignKey('java_api_html_text.id'), unique=True, nullable=False)
    text = Column(LONGTEXT(), nullable=True)  # text with no html tags
    valid = Column(Integer, default=1, index=True)  # is the paragraph valid

    __table_args__ = (Index('api_id_text_type_index', html_text_id), {
        "mysql_charset": "utf8",
    })

    def __init__(self, html_text_id, text):
        self.html_text_id = html_text_id
        self.text = text

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    @staticmethod
    def get_doc_list(session):
        try:
            doc_list = session.query(DocumentText).all()
            return doc_list
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_by_id(session, id):
        try:
            return session.query(DocumentText).filter_by(id=id).first()
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_by_html_text_id(session, html_text_id):
        try:
            document_list = session.query(DocumentText).filter_by(html_text_id=html_text_id).first()
            return document_list
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_all_valid_document(session):
        try:
            document_list = session.query(DocumentText).filter_by(valid=1).all()
            return document_list
        except Exception:
            traceback.print_exc()
            return []


class SentenceToParagraphRelation(Base):
    __tablename__ = 'java_api_document_sentence_to_paragraph_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    paragraph_id = Column(Integer, ForeignKey('java_api_document_paragraph_text.id'), nullable=False, index=True)
    sentence_id = Column(Integer, ForeignKey('java_api_document_sentence_text.id'), nullable=False, index=True)

    __table_args__ = (Index('paragraph_id_sentence_id', paragraph_id, sentence_id), {
        "mysql_charset": "utf8",
    })

    def __init__(self, paragraph_id, sentence_id):
        self.paragraph_id = paragraph_id
        self.sentence_id = sentence_id

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(SentenceToParagraphRelation).filter_by(paragraph_id=self.paragraph_id,
                                                                            sentence_id=self.sentence_id).first()
            except Exception:
                # traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    @staticmethod
    def exist_import_record(session, paragraph_id, sentence_id):
        """
        check if the start_row_id has map in end_knowledge_table

        """

        try:
            team = session.query(SentenceToParagraphRelation).filter_by(paragraph_id=paragraph_id,
                                                                        sentence_id=sentence_id).first()
            if team:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False


class DocumentParagraphText(Base):
    __tablename__ = 'java_api_document_paragraph_text'
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey('java_api_document_text.id'), nullable=False, index=True)
    paragraph_index = Column(Integer, nullable=True)  # text with no html tags
    text = Column(Text(), nullable=True)  # text with no html tags
    valid = Column(Integer, default=1, index=True)  # is the paragraph valid

    __table_args__ = (Index('doc_id_paragraph_index', doc_id, paragraph_index), {
        "mysql_charset": "utf8",
    })

    def __init__(self, doc_id, paragraph_index, text):
        self.doc_id = doc_id
        self.paragraph_index = paragraph_index
        self.text = text

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(DocumentParagraphText).filter_by(doc_id=self.doc_id,
                                                                      paragraph_index=self.paragraph_index).first()
            except Exception:
                # traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    @staticmethod
    def get_first_by_doc_id(session, doc_id):
        try:
            team = session.query(DocumentParagraphText).filter_by(doc_id=doc_id, paragraph_index=0
                                                                  ).first()
            return team
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def exist_import_record(session, doc_id, paragraph_index):
        """
        check if the start_row_id has map in end_knowledge_table

        """

        try:
            team = session.query(DocumentParagraphText).filter_by(doc_id=doc_id,
                                                                  paragraph_index=paragraph_index).first()
            if team:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    @staticmethod
    def get_id_by_doc_id_and_paragraph_index(session, doc_id, paragraph_index):
        try:
            paragraph_id = session.query(DocumentParagraphText.id).filter_by(doc_id=doc_id,
                                                                             paragraph_index=paragraph_index).scalar()
            return paragraph_id
        except Exception:
            traceback.print_exc()
            return -1

    @staticmethod
    def get_all_paragraph_text(session):
        try:
            # todo,make this api only return valid paragraph text list
            return session.query(DocumentParagraphText).all()
        except Exception:
            traceback.print_exc()
            return []

    @staticmethod
    def get_all_valid_paragraph(session):
        try:
            paragraph_list = session.query(DocumentParagraphText).filter_by(valid=1).all()
            return paragraph_list
        except Exception:
            traceback.print_exc()
            return []


class DocumentSentenceText(FullText, Base):
    __tablename__ = 'java_api_document_sentence_text'
    __fulltext_columns__ = ('text',)
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey('java_api_document_text.id'), nullable=False, index=True)
    sentence_index = Column(Integer, nullable=True)  # text with no html tags
    text = Column(Text(), nullable=True)  # text with no html tags
    valid = Column(Integer, default=1, index=True)  # is the paragraph valid

    __table_args__ = (Index('doc_id_sentence_index', doc_id, sentence_index), {
        "mysql_charset": "utf8",
    })

    def __init__(self, doc_id=None, sentence_index=None, text=None):
        self.doc_id = doc_id
        self.sentence_index = sentence_index
        self.text = text

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    @staticmethod
    def exist_import_record(session, doc_id, sentence_index):
        """
        check if the start_row_id has map in end_knowledge_table

        """

        try:
            team = session.query(DocumentSentenceText).filter_by(doc_id=doc_id,
                                                                 sentence_index=sentence_index).first()
            if team:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    @staticmethod
    def get_sentence_list_by_doc_id(session, doc_id):
        try:
            sentence_list = session.query(DocumentSentenceText).filter_by(doc_id=doc_id).all()
            return sentence_list
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_doc_id_by_sentence_id(session, sentence_id):
        try:
            sentence = session.query(DocumentSentenceText).filter_by(id=sentence_id).all()
            return sentence
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_all_valid_sentences(session):
        try:
            sentence_list = session.query(DocumentSentenceText).filter_by(valid=1).all()
            return sentence_list
        except Exception:
            traceback.print_exc()
            return []

    @staticmethod
    def is_valid(session, sentence_id):
        try:
            sentence = session.query(DocumentSentenceText.id).filter_by(id=sentence_id, valid=1).first()
            if sentence:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    @staticmethod
    def get_valid_sentence(session, sentence_id):
        try:
            sentence = session.query(DocumentSentenceText).filter_by(id=sentence_id, valid=1).first()
            return sentence
        except Exception:
            traceback.print_exc()
            return None


class DocumentSentenceTextAnnotation(Base):
    __tablename__ = 'java_api_document_sentence_text_annotation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey('java_api_document_text.id'), nullable=False, index=True)
    sentence_index = Column(Integer, nullable=True)  # text with no html tags
    text = Column(Text(), nullable=True)  # text with no html tags
    type = Column(Integer, nullable=True, index=True)  # annotated type
    username = Column(String(64), nullable=True)

    __table_args__ = (Index('doc_id_sentence_index', doc_id, sentence_index), {
        "mysql_charset": "utf8",
    })

    ANNOTATED_TYPE_FUNCTIONALITY = 1
    ANNOTATED_TYPE_DIRECTIVE = 2
    ANNOTATED_TYPE_EXPLANATION = 3  # or Concept
    ANNOTATED_TYPE_OTHERS = 0

    def __init__(self, doc_id, sentence_index, type, username):
        self.doc_id = doc_id
        self.sentence_index = sentence_index
        self.type = type
        self.username = username

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(DocumentSentenceTextAnnotation).filter_by(doc_id=self.doc_id,
                                                                               sentence_index=self.sentence_index,
                                                                               username=self.username).first()
            except Exception:
                # traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            if remote_instance.type != self.type:
                remote_instance.type = self.type
            if autocommit:
                session.commit()
            return remote_instance

    @staticmethod
    def exist_import_record(session, doc_id, sentence_index):
        """
        check if the start_row_id has map in end_knowledge_table
        """
        try:
            team = session.query(DocumentSentenceText).filter_by(doc_id=doc_id,
                                                                 sentence_index=sentence_index).first()
            if team:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    @staticmethod
    def get_annotation_count_by_index(session, doc_id, sentence_index):
        try:
            annotation_list = session.query(DocumentSentenceTextAnnotation).filter_by(doc_id=doc_id,
                                                                                      sentence_index=sentence_index)
            annotation_count = annotation_list.with_entities(func.count(DocumentSentenceTextAnnotation.id)).scalar()
            if annotation_count:
                return annotation_count
            else:
                return -1
        except Exception:
            traceback.print_exc()
            return -1

    @staticmethod
    def get_type_string(type_code):
        if type_code == DocumentSentenceTextAnnotation.ANNOTATED_TYPE_FUNCTIONALITY:
            return "functionality"
        if type_code == DocumentSentenceTextAnnotation.ANNOTATED_TYPE_DIRECTIVE:
            return "directive"
        if type_code == DocumentSentenceTextAnnotation.ANNOTATED_TYPE_EXPLANATION:
            return "explanation"
        return "others"


class APIInstanceEntityRelation(Base):
    __tablename__ = 'java_api_value_instance_entity_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_instance_id = Column(Integer, ForeignKey('java_api_value_instance_entity.id'), nullable=False, index=True)
    end_instance_id = Column(Integer, ForeignKey('java_api_value_instance_entity.id'), nullable=False, index=True)
    relation_type = Column(Integer, index=True)

    __table_args__ = (Index('unique_index', start_instance_id, end_instance_id, relation_type),
                      Index('all_relation_index', start_instance_id, end_instance_id),
                      {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, start_instance_id, end_instance_id, relation_type):
        self.start_instance_id = start_instance_id
        self.end_instance_id = end_instance_id
        self.relation_type = relation_type

    def exist_in_remote(self, session):
        try:
            if session.query(APIInstanceEntityRelation.id).filter_by(start_instance_id=self.start_instance_id,
                                                                     end_instance_id=self.end_instance_id,
                                                                     relation_type=self.relation_type).first():
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIInstanceEntityRelation).filter_by(start_instance_id=self.start_instance_id,
                                                                          end_instance_id=self.end_instance_id,
                                                                          relation_type=self.relation_type).first()
            except Exception:
                # traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def __repr__(self):
        return '<APIInstanceEntityRelation: %r-%r: type=%r >' % (
            self.start_instance_id, self.end_instance_id, self.relation_type)


class APIInstanceEntity(Base):
    TYPE_UNKNOWN = 0
    TYPE_RETURN_VALUE = 1
    TYPE_PARAMETER = 2

    __tablename__ = 'java_api_value_instance_entity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    instance_type = Column(Integer, default=TYPE_UNKNOWN, index=True)
    simple_type = Column(String(1024), index=True)
    qualified_type = Column(String(1024), index=True)
    formal_parameter_name = Column(String(1024), nullable=True, index=True)
    qualified_full_name = Column(String(1024), index=True)
    simple_full_name = Column(String(1024), index=True)
    short_description = Column(Text(1024), nullable=True, index=True)
    out_relation = relationship('APIInstanceEntityRelation', foreign_keys=[APIInstanceEntityRelation.start_instance_id],
                                backref='start_api_instance')
    in_relation = relationship('APIInstanceEntityRelation', foreign_keys=[APIInstanceEntityRelation.end_instance_id],
                               backref='end_api_instance')

    __table_args__ = {
        "mysql_charset": "utf8"
    }

    def __init__(self, simple_type, qualified_type, formal_parameter_name, qualified_full_name, simple_full_name):
        self.simple_type = simple_type
        self.qualified_type = qualified_type
        self.formal_parameter_name = formal_parameter_name
        self.qualified_full_name = qualified_full_name
        self.simple_full_name = simple_full_name

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIInstanceEntity).filter(
                    APIInstanceEntity.qualified_full_name == func.binary(self.qualified_full_name)).first()
            except Exception:
                traceback.print_exc()
                return None

    def __repr__(self):
        return '<APIInstanceEntity: id=%r qualified_full_name=%r>' % (self.id, self.qualified_full_name)

    def __hash__(self):
        return hash(self.id)


class APIInstanceToAPIEntityRelation(Base):
    DIRECTION_INSTANCE_TO_API = 0
    DIRECTION_API_TO_INSTANCE = 1

    RELATION_TYPE_TYPE_OF = 1
    RELATION_TYPE_HAS_PARAMETER = 2
    RELATION_TYPE_RETURN = 3

    __tablename__ = 'instance_entity_to_api_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    instance_entity_id = Column(Integer, ForeignKey('java_api_value_instance_entity.id'), nullable=False, index=True)
    api_id = Column(Integer, ForeignKey('java_all_api_entity.id'), nullable=False, index=True)
    relation_type = Column(Integer, index=True)
    relation_direction = Column(Integer, default=DIRECTION_INSTANCE_TO_API, index=True)

    __table_args__ = (Index('unique_index', instance_entity_id, api_id, relation_type, relation_direction),
                      Index('all_relation_index', instance_entity_id, api_id),
                      {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, start_instance_id, end_instance_id, relation_type):
        self.start_instance_id = start_instance_id
        self.end_instance_id = end_instance_id
        self.relation_type = relation_type

    def exist_in_remote(self, session):
        try:
            if session.query(APIInstanceEntityRelation.id).filter_by(start_instance_id=self.start_instance_id,
                                                                     end_instance_id=self.end_instance_id,
                                                                     relation_type=self.relation_type).first():
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIInstanceEntityRelation).filter_by(start_instance_id=self.start_instance_id,
                                                                          end_instance_id=self.end_instance_id,
                                                                          relation_type=self.relation_type).first()
            except Exception:
                # traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def __repr__(self):
        return '<APIInstanceEntityRelation: %r-%r: type=%r >' % (
            self.start_instance_id, self.end_instance_id, self.relation_type)


class SentenceToAPIEntityRelation(Base):
    RELATION_TYPE_SOURCE_FROM = 1
    __tablename__ = 'sentence_to_api_entity_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(Integer, ForeignKey('java_api_document_sentence_text.id'), nullable=False, index=True)
    api_id = Column(Integer, ForeignKey('java_all_api_entity.id'), nullable=False, index=True)
    relation_type = Column(Integer, index=True, default=RELATION_TYPE_SOURCE_FROM)

    __table_args__ = (
        Index('all_relation_index', api_id, sentence_id),
        {
            "mysql_charset": "utf8",
        })

    def __init__(self, sentence_id, api_id, relation_type=RELATION_TYPE_SOURCE_FROM):
        self.sentence_id = sentence_id
        self.api_id = api_id
        self.relation_type = relation_type

    def exist_in_remote(self, session):
        try:
            if session.query(SentenceToAPIEntityRelation.id).filter_by(sentence_id=self.sentence_id,
                                                                       api_id=self.api_id,
                                                                       relation_type=self.relation_type).first():
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(SentenceToAPIEntityRelation).filter_by(sentence_id=self.sentence_id,
                                                                            api_id=self.api_id,
                                                                            relation_type=self.relation_type).first()
            except Exception:
                # traceback.print_exc()
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def __repr__(self):
        return '<SentenceToAPIEntityRelation: %r-%r: type=%r >' % (
            self.sentence_id, self.api_id, self.relation_type)


class SentenceToMergeNPEntityRelation(Base):
    __tablename__ = 'sentence_to_merge_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(Integer, ForeignKey('java_api_document_sentence_text.id'), nullable=False, index=True)
    merge_np_id = Column(Integer, ForeignKey('java_documnet_noun_phase_merge_clean.id'), nullable=False, index=True)

    __table_args__ = (
        Index('sentence_to_merge_np_index', merge_np_id, sentence_id),
        {
            "mysql_charset": "utf8",
        })

    def __init__(self, sentence_id, merge_np_id):
        self.sentence_id = sentence_id
        self.merge_np_id = merge_np_id

    def exist_in_remote(self, session):
        try:
            if session.query(SentenceToMergeNPEntityRelation.id).filter_by(sentence_id=self.sentence_id,
                                                                           merge_np_id=self.merge_np_id,
                                                                           ).first():
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(SentenceToMergeNPEntityRelation).filter_by(sentence_id=self.sentence_id,
                                                                                merge_np_id=self.merge_np_id).first()
            except Exception:
                return None

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def __repr__(self):
        return '<SentenceToMergeNPEntityRelation: %r-%r>' % (self.sentence_id, self.merge_np_id)

    @staticmethod
    def get_all_relation_by_merge_np_id(session, merge_np_id):

        return session.query(SentenceToMergeNPEntityRelation).filter_by(
            merge_np_id=merge_np_id).all()

    @staticmethod
    def delete_all(session):
        try:
            session.query(SentenceToMergeNPEntityRelation).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return


class LibraryEntity(Base):
    __tablename__ = 'library_entity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), index=True)
    version = Column(String(128), nullable=True)
    short_description = Column(Text(), nullable=True)
    url = Column(String(512), nullable=True, index=True)

    __table_args__ = (Index('name_url_index', "name", "url"), {
        "mysql_charset": "utf8",
    })

    def __init__(self, name, version, short_description, url):
        self.name = name
        self.version = version
        self.short_description = short_description
        self.url = url

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(LibraryEntity).filter_by(name=self.name, url=self.url).first()
            except Exception:
                # traceback.print_exc()
                return None


class APIBelongToLibraryRelation(Base):
    __tablename__ = 'api_belong_to_library_relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey('java_all_api_entity.id'), nullable=False)
    library_id = Column(Integer, ForeignKey('library_entity.id'), nullable=False)
    __table_args__ = (Index('belong_to_index', api_id, library_id), {
        "mysql_charset": "utf8",
    })

    def __init__(self, api_id, library_id):
        self.api_id = api_id
        self.library_id = library_id

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(APIBelongToLibraryRelation).filter_by(api_id=self.api_id,
                                                                           library_id=self.library_id).first()
            except Exception:
                traceback.print_exc()
                return None


class KnowledgeTable(Base):
    __tablename__ = 'knowledge_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String(30), nullable=False)
    schema = Column(String(128), nullable=False)
    table_name = Column(String(128), nullable=False, index=True)
    description = Column(Text(), nullable=True)
    create_time = Column(DateTime(), nullable=True)

    __table_args__ = {
        "mysql_charset": "utf8"
    }

    def __init__(self, ip, schema, table_name, description):
        self.ip = ip
        self.schema = schema
        self.table_name = table_name
        self.description = description
        self.create_time = datetime.now()

    def find_or_create(self, session, autocommit=True):
        remote_instance = self.get_remote_object(session)
        if not remote_instance:
            session.add(self)
            if autocommit:
                session.commit()
            return self
        else:
            return remote_instance

    def get_remote_object(self, session):
        if self.id:
            return self
        else:
            try:
                return session.query(KnowledgeTable).filter_by(ip=self.ip, schema=self.schema,
                                                               table_name=self.table_name).one()
            except Exception:
                # traceback.print_exc()
                return None


class KnowledgeTableRowMapRecord(Base):
    __tablename__ = 'knowledge_table_row_map'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_table_id = Column(Integer, ForeignKey('knowledge_table.id'), nullable=False)
    end_table_id = Column(Integer, ForeignKey('knowledge_table.id'), nullable=False)
    start_row_id = Column(Integer, nullable=False, index=True)
    end_row_id = Column(Integer, nullable=False, index=True)
    valid = Column(Boolean, nullable=False, index=True, default=True)
    create_time = Column(DateTime(), nullable=False, index=True)

    __table_args__ = (Index('start_id_index', "start_table_id", "end_table_id", start_row_id),
                      Index('end_id_index', "start_table_id", "end_table_id", end_row_id), {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, start_knowledge_table, end_knowledge_table, start_row_id, end_row_id):
        self.start_table_id = start_knowledge_table.id
        self.end_table_id = end_knowledge_table.id
        self.start_row_id = start_row_id
        self.end_row_id = end_row_id
        self.create_time = datetime.now()

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    @staticmethod
    def exist_import_record(session, start_knowledge_table, end_knowledge_table, start_row_id):
        """
        check if the start_row_id has map in end_knowledge_table
        :param session:
        :param start_knowledge_table:
        :param end_knowledge_table:
        :param start_row_id:
        :return:
        """

        try:
            team = session.query(KnowledgeTableRowMapRecord).filter_by(start_table_id=start_knowledge_table.id,
                                                                       end_table_id=end_knowledge_table.id,
                                                                       start_row_id=start_row_id).first()
            if team:
                return True
            else:
                return False
        except Exception:
            # traceback.print_exc()
            return False

    @staticmethod
    def get_end_row_id(session, start_knowledge_table, end_knowledge_table, start_row_id):
        """
        check if the start_row_id has map in end_knowledge_table
        :param session:
        :param start_knowledge_table:
        :param end_knowledge_table:
        :param start_row_id:
        :return:
        """

        try:
            end_row_id = session.query(KnowledgeTableRowMapRecord.end_row_id).filter_by(
                start_table_id=start_knowledge_table.id,
                end_table_id=end_knowledge_table.id,
                start_row_id=start_row_id).scalar()
            return end_row_id
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def get_transformed_table_data(session, start_knowledge_table, end_knowledge_table):
        try:
            data_list = session.query(KnowledgeTableRowMapRecord).filter_by(
                start_table_id=start_knowledge_table.id,
                end_table_id=end_knowledge_table.id).all()
            return data_list
        except Exception:
            traceback.print_exc()
            return None


class PostsRecord(Base, FullText):
    __tablename__ = 'posts'
    __fulltext_columns__ = ('title',)

    id = Column(Integer, primary_key=True, autoincrement=True, name="Id")
    post_type_id = Column(SmallInteger, name="PostTypeId")
    accepted_answer_id = Column(Integer, name="AcceptedAnswerId")
    parent_id = Column(Integer, name="ParentId")
    score = Column(Integer, name="Score")
    view_count = Column(Integer, name="ViewCount")
    body = Column(Text(), name="Body")
    owner_user_id = Column(Integer, name="OwnerUserId")
    owner_display_name = Column(String(256), name="OwnerDisplayName")
    last_editor_user_id = Column(Integer, name="LastEditorUserId")
    last_edit_date = Column(DateTime(), name="LastEditDate")
    last_activity_date = Column(DateTime(), name="LastActivityDate")
    title = Column(String(256), name="Title")
    tags = Column(String(256), name="Tags")
    answer_count = Column(Integer, name="AnswerCount")
    comment_count = Column(Integer, name="CommentCount")
    favorite_count = Column(Integer, name="FavoriteCount")
    creation_date = Column(DateTime(), name="CreationDate")

    __table_args__ = ({
        "mysql_charset": "utf8",
    })

    def __init__(self, session=None):
        self.session = session
        if self.session is None:
            self.session = self.get_so_session()

    def get_so_session(self):
        if not self.session:
            self.session = EngineFactory.create_so_session()

        return self.session

    def get_post_by_id(self, id_num):
        post_id_node = self.session.query(PostsRecord).get(id_num)

        post = {
            "id": post_id_node.id,
            "post_type_id": post_id_node.post_type_id,
            "accepted_answer_id": post_id_node.accepted_answer_id,
            "parent_id": post_id_node.parent_id,
            "score": post_id_node.score,
            "body": post_id_node.body,
            "owner_user_id": post_id_node.owner_user_id,
            "owner_display_name": post_id_node.owner_display_name,
            "last_editor_user_id": post_id_node.last_editor_user_id,
            "last_activity_date": post_id_node.last_activity_date,
            "title": post_id_node.title,
            "tags": post_id_node.tags,
            "answer_count": post_id_node.answer_count,
            "comment_count": post_id_node.comment_count,
            "favorite_count": post_id_node.favorite_count,
            "creation_date": post_id_node.creation_date,
        }
        return post

    def __repr__(self):
        return '<POSTS: id=%r score=%r title=%r tags=%r>' % (self.id, self.score, self.title, self.tags)


class KnowledgeTableColumnMapRecord(Base):
    __tablename__ = 'knowledge_table_row_column_map'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_table_id = Column(Integer, ForeignKey('knowledge_table.id'), nullable=False)
    end_table_id = Column(Integer, ForeignKey('knowledge_table.id'), nullable=False)
    start_row_name = Column(String(128), nullable=False, index=True)
    start_row_id = Column(Integer, nullable=False, index=True)
    end_row_id = Column(Integer, nullable=False, index=True)
    valid = Column(Boolean, nullable=False, index=True, default=True)
    create_time = Column(DateTime(), nullable=False, index=True)

    __table_args__ = (Index('start_id_index', start_table_id, end_table_id, start_row_id, start_row_name),
                      Index('end_id_index', start_table_id, end_table_id, end_row_id, start_row_name),
                      {
                          "mysql_charset": "utf8",
                      })

    def __init__(self, start_knowledge_table, end_knowledge_table, start_row_id, end_row_id, start_row_name):
        self.start_table_id = start_knowledge_table.id
        self.end_table_id = end_knowledge_table.id
        self.start_row_id = start_row_id
        self.end_row_id = end_row_id
        self.start_row_name = start_row_name
        self.create_time = datetime.now()

    def create(self, session, autocommit=True):
        session.add(self)
        if autocommit:
            session.commit()
        return self

    @staticmethod
    def exist_import_record(session, start_knowledge_table, end_knowledge_table, start_row_id, start_row_name):
        """
        check if the start_row_id has map in end_knowledge_table
        :param session:
        :param start_knowledge_table:
        :param end_knowledge_table:
        :param start_row_id:
        :return:
        """

        try:
            team = session.query(KnowledgeTableColumnMapRecord).filter_by(start_table_id=start_knowledge_table.id,
                                                                          end_table_id=end_knowledge_table.id,
                                                                          start_row_id=start_row_id,
                                                                          start_row_name=start_row_name).first()
            if team:
                return True
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    @staticmethod
    def get_end_row_id(session, start_knowledge_table, end_knowledge_table, start_row_id, start_row_name):
        """
        check if the start_row_id has map in end_knowledge_table
        :param session:
        :param start_knowledge_table:
        :param end_knowledge_table:
        :param start_row_id:
        :return:
        """

        try:
            end_row_id = session.query(KnowledgeTableColumnMapRecord.end_row_id).filter_by(
                start_table_id=start_knowledge_table.id,
                end_table_id=end_knowledge_table.id,
                start_row_id=start_row_id,
                start_row_name=start_row_name).scalar()
            return end_row_id
        except Exception:
            # traceback.print_exc()
            return None


class EntityForQA(Base, FullText):
    __tablename__ = 'entity_for_qa'
    __fulltext_columns__ = ('attr_value',)
    table_id = Column(Integer, primary_key=True, autoincrement=True)
    kg_id = Column(Integer, index=True, nullable=False)
    entity_id = Column(Integer, index=True, nullable=True)
    attr_value = Column(String(512), index=True, nullable=False)
    attr = Column(String(64), index=True, nullable=False)
    source = Column(String(64), index=True, nullable=False)

    def __init__(self, kg_id=None, entity_id=None, source=None, attr=None, attr_value=None):
        self.kg_id = kg_id
        self.entity_id = entity_id
        self.source = source
        self.attr = attr
        self.attr_value = attr_value

    @staticmethod
    def clear_table(session):
        sql_str = 'truncate table entity_for_qa'
        session.execute(sql_str)
        session.commit()
        print("clear table")

    def insert(self, session):
        session.add(self)
        session.commit()

    @staticmethod
    def delete_names_by_source(session, source):
        try:
            session.query(EntityForQA).filter(EntityForQA.source == source).delete()
            session.commit()
        except Exception:
            traceback.print_exc()
            return

    def __repr__(self):
        return '<EntityForQA: %r-%r-%r>' % (self.source, self.attr, self.attr_value)

    def __hash__(self):
        return self.table_id

    def __eq__(self, other):
        # another object is equal to self, iff
        # it is an instance of MyClass
        return isinstance(other, EntityForQA)

def parse_api_type_string_to_api_type_constant(api_type_string):
    if api_type_string == "Method":
        return APIEntity.API_TYPE_METHOD
    if api_type_string == "Constructor":
        return APIEntity.API_TYPE_CONSTRUCTOR
    if api_type_string == "Nested":
        return APIEntity.API_TYPE_CLASS
    if api_type_string == "Required":
        return APIEntity.API_TYPE_FIELD
    if api_type_string == "Optional":
        return APIEntity.API_TYPE_FIELD
    if api_type_string == "Field":
        return APIEntity.API_TYPE_FIELD
    if api_type_string == "Enum":
        return APIEntity.API_TYPE_ENUM_CONSTANTS

    api_type = APIEntity.API_TYPE_UNKNOWN
    return api_type


if __name__ == "__main__":
    engine = EngineFactory.create_engine_to_center()
    metadata = MetaData(bind=engine)
    # delete all table
    # Base.metadata.drop_all(bind=engine)

    # create the table
    Base.metadata.create_all(bind=engine)
