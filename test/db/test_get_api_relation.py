from unittest import TestCase

from db.engine_factory import EngineFactory
from db.model import APIEntity


class TestGet_api_relation(TestCase):
    def test_get_api_relation(self):
        session = EngineFactory.create_session()
        api = APIEntity.find_by_id(session, 462)
        api=APIEntity.find_by_qualifier(session,"java.lang.String")
        print "api =", api
        print api.document_websites
        print "out_relation"
        for r in api.out_relation:
            print r
            print "start_api=", r.start_api
            print "end_api=", r.end_api
            print "------------"

        print "in_relation"

        for r in api.in_relation:
            print r
            print "start_api=", r.start_api
            print "end_api=", r.end_api
            print "------------"

            # api_entity_alias=APIEntity.find_by_id(session,1)
            # print api_entity_alias

