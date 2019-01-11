from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import APIDocumentWebsite, KnowledgeTableRowMapRecord, APIRelation
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_doc_website_for_jdk_method").get_log()
cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()
jdk_method_knowledge_table = KnowledgeTableFactory.get_jdk_method_table(session)
api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)


def get_see_also_data():
    sql = "select see_also_website, method_id from api_doc.jdk_method_see_also"
    cur.execute(sql)
    see_also_data = cur.fetchall()
    return see_also_data


def import_jdk_see_also_relation_for_method():
    see_also_data = get_see_also_data()
    # print see_also_data
    for each in see_also_data:
        see_also_website = each[0]
        original_method_id = each[1]
        end_api_id = APIDocumentWebsite.get_api_id_by_website(session, see_also_website)
        # print see_also_website, " ", end_api_id
        start_api_id = KnowledgeTableRowMapRecord.get_end_row_id(session, jdk_method_knowledge_table, api_knowledge_table, original_method_id)
        # print start_api_id
        if end_api_id is not None and start_api_id is not None:
            api_relation = APIRelation(start_api_id, end_api_id, APIRelation.RELATION_TYPE_SEE_ALSO)
            api_relation.find_or_create(session, autocommit=False)
            print original_method_id, "-------------------------------", api_relation
    session.commit()


if __name__ == "__main__":
    import_jdk_see_also_relation_for_method()
