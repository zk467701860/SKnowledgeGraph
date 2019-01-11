#!/usr/bin/env python
# -*- coding: utf-8 -*-s
import unittest

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import FullText, FullTextSearch, FullTextForMigration
import modes as FullTextMode

FULLTEXT_TABLE = "test_full_text"
FULLTEXT_TABLE_FOR_MIGRATION = "test_full_text_for_migration"
BASE = declarative_base()

try:
    ENGINE = create_engine('mysql+mysqldb://travis@localhost/test_full_text?charset=utf8', echo=True)
except ImportError:
    ENGINE = create_engine('mysql+pymysql://travis@localhost/test_full_text?charset=utf8', echo=True)

SESSION = sessionmaker(bind=ENGINE)()
SESSION.execute('DROP TABLE IF EXISTS {0};'.format(FULLTEXT_TABLE))
SESSION.execute('DROP TABLE IF EXISTS {0};'.format(FULLTEXT_TABLE_FOR_MIGRATION))

MYSQL_ENGINES = [i[0] for i in SESSION.execute('SHOW ENGINES;').fetchall()
                if i[1] == "YES"]
MYSQL_VERSION = SESSION.execute('SHOW VARIABLES LIKE "version";').fetchone()[1]

class RecipeReviewModel(FullText, BASE):

    __tablename__ = FULLTEXT_TABLE
    # mroonga engine supporting CJK chars
    __table_args__ = {'mysql_engine':'MyISAM',
                      'mysql_charset':'utf8'}

    __fulltext_columns__ = ('commentor','review')

    id        = Column(Integer,primary_key=True)
    commentor = Column(String(length=100))
    review    = Column(Text())

    def __init__(self, commentor, review):
        self.review = review
        self.commentor = commentor


class RecipeReviewModelForMigration(FullTextForMigration, BASE):
    __tablename__ = FULLTEXT_TABLE_FOR_MIGRATION
    # mroonga engine supporting CJK chars
    __table_args__ = {'mysql_engine': 'MyISAM',
                      'mysql_charset': 'utf8'}

    __fulltext_columns__ = ('commentor', 'review')

    id = Column(Integer, primary_key=True)
    commentor = Column(String(length=100))
    review = Column(Text())

    def __init__(self, commentor, review):
        self.review = review
        self.commentor = commentor


RecipeReviewModelForMigration.index_fulltext()


class TestSQLAlchemyFullText(unittest.TestCase):

    def setUp(self):
        self.base = BASE
        self.engine = ENGINE
        self.session = SESSION


        self.entries = []

    def test_fulltext_abuild(self):
        self.assertIsNone(self.base.metadata.create_all(self.engine))

    def test_fulltext_add(self):
        import json
        with open('test_fulltext.json') as fp:
            bulk = json.load(fp)
            for entry in bulk:
                self.entries.append(RecipeReviewModel(
                                entry['commentor'],
                                entry['review']))
                self.entries.append(RecipeReviewModelForMigration(
                                entry['commentor'],
                                entry['review']))

        for entry in self.entries:
            self.assertIsNone( self.session.add(entry))
        self.session.commit()
    def test_fulltext_form_query(self):
        FullTextSearch('spam', RecipeReviewModel)
        FullTextSearch('spam', RecipeReviewModelForMigration)

    def test_fulltext_query(self):
        full = self.session.query(RecipeReviewModel).filter(FullTextSearch('spam', RecipeReviewModel))
        self.assertEqual(full.count(), 2,)
        full = self.session.query(RecipeReviewModelForMigration).filter(FullTextSearch('spam', RecipeReviewModelForMigration))
        self.assertEqual(full.count(), 2,)
        raw = self.session.execute('SELECT * FROM {0} WHERE MATCH (commentor, review) AGAINST ("spam")'.format(RecipeReviewModel.__tablename__))
        self.assertEqual(full.count(), raw.rowcount, 'Query Test Failed')

    def test_fulltext_qutoe_query(self):
        full = self.session.query(RecipeReviewModel).filter(FullTextSearch('"parrot can"', RecipeReviewModel, FullTextMode.BOOLEAN))
        self.assertEqual(full.count(), 2,)
        full = self.session.query(RecipeReviewModelForMigration).filter(FullTextSearch('"parrot can"', RecipeReviewModelForMigration, FullTextMode.BOOLEAN))
        self.assertEqual(full.count(), 2,)
        raw = self.session.execute("""SELECT * FROM {0} WHERE MATCH (commentor, review) AGAINST ('"parrot can"' IN BOOLEAN MODE)""".format(RecipeReviewModel.__tablename__))
        self.assertEqual(full.count(), raw.rowcount)

    @unittest.skipIf(not 'mroonga' in MYSQL_ENGINES, 'mroonga engines not available')
    def test_fulltext_cjk_query(self):
        cjk = self.session.query(RecipeReviewModel).filter(
                                  FullTextSearch('中国人'.decode('utf8'),
                                                 RecipeReviewModel))
        cjk = self.session.query(RecipeReviewModelForMigration).filter(
                                  FullTextSearch('中国人'.decode('utf8'),
                                                 RecipeReviewModelForMigration))


    def test_fulltext_query_natural_mode(self):
        full = self.session.query(RecipeReviewModel).filter(FullTextSearch('spam', RecipeReviewModel, FullTextMode.NATURAL))
        self.assertEqual(full.count(), 2,)
        full = self.session.query(RecipeReviewModelForMigration).filter(FullTextSearch('spam', RecipeReviewModelForMigration, FullTextMode.NATURAL))
        self.assertEqual(full.count(), 2,)
        raw = self.session.execute('SELECT * FROM {0} WHERE MATCH (commentor, review) AGAINST ("spam" IN NATURAL LANGUAGE MODE)'.format(RecipeReviewModel.__tablename__))
        self.assertEqual(full.count(), raw.rowcount, 'Query Test Failed')

    def test_fulltext_query_boolean_mode(self):
        full = self.session.query(RecipeReviewModel).filter(FullTextSearch('spa*', RecipeReviewModel, FullTextMode.BOOLEAN))
        self.assertEqual(full.count(), 3,)
        full = self.session.query(RecipeReviewModelForMigration).filter(FullTextSearch('spa*', RecipeReviewModelForMigration, FullTextMode.BOOLEAN))
        self.assertEqual(full.count(), 3,)
        raw = self.session.execute('SELECT * FROM {0} WHERE MATCH (commentor, review) AGAINST ("spa*" IN BOOLEAN MODE)'.format(RecipeReviewModel.__tablename__))
        self.assertEqual(full.count(), raw.rowcount, 'Query Test Failed')

    def test_github_issue_9(self):
        # https://github.com/mengzhuo/sqlalchemy-fulltext-search/issues/9
        full = self.session.query(RecipeReviewModel).filter(RecipeReviewModel.id >= 1)
        full = full.filter(FullTextSearch('the -rainbow', RecipeReviewModel, FullTextMode.BOOLEAN)).limit(20)
        self.assertEqual(full.count(), 0)
        raw = self.session.execute('SELECT * FROM {0} WHERE MATCH (commentor, review) AGAINST ("the -rainbow" IN BOOLEAN MODE)'.format(RecipeReviewModel.__tablename__))
        self.assertEqual(full.count(), raw.rowcount, 'Query Test Failed')

        full = self.session.query(RecipeReviewModelForMigration).filter(RecipeReviewModelForMigration.id >= 1)
        full = full.filter(FullTextSearch('the -rainbow', RecipeReviewModelForMigration, FullTextMode.BOOLEAN)).limit(20)
        self.assertEqual(full.count(), 0)
        raw = self.session.execute('SELECT * FROM {0} WHERE MATCH (commentor, review) AGAINST ("the -rainbow" IN BOOLEAN MODE)'.format(RecipeReviewModelForMigration.__tablename__))
        self.assertEqual(full.count(), raw.rowcount, 'Query Test Failed')


    def test_fulltext_query_query_expansion_mode(self):
        full = self.session.query(RecipeReviewModel).filter(FullTextSearch('spam', RecipeReviewModel, FullTextMode.QUERY_EXPANSION))
        self.assertEqual(full.count(), 3,)
        full = self.session.query(RecipeReviewModelForMigration).filter(FullTextSearch('spam', RecipeReviewModelForMigration, FullTextMode.QUERY_EXPANSION))
        self.assertEqual(full.count(), 3,)
        raw = self.session.execute('SELECT * FROM {0} WHERE MATCH (commentor, review) AGAINST ("spam" WITH QUERY EXPANSION)'.format(RecipeReviewModel.__tablename__))
        self.assertEqual(full.count(), raw.rowcount, 'Query Test Failed')

if __name__ == '__main__':
    unittest.main()
