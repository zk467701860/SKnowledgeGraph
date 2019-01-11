from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIRelation
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_throw_exception_for_jdk_method").get_log()
cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()
jdk_method_knowledge_table = KnowledgeTableFactory.get_jdk_method_table(session)
api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)
jdk_class_knowledge_table = KnowledgeTableFactory.get_jdk_class_table(session)


def get_jdk_exception_data():
    sql = "select name, method_id from api_doc.jdk_exception"
    cur.execute(sql)
    jdk_exception_data = cur.fetchall()
    return jdk_exception_data


def get_class_id_by_exception_name(exception_name):
    if exception_name is not None and exception_name != "":
        sql = 'select class_id from api_doc.jdk_class where class_name = "' + exception_name + '"'
        cur.execute(sql)
        class_id_data = cur.fetchone()
        if class_id_data is not None:
            class_id = class_id_data[0]
            return class_id
    return None


def import_jdk_throw_exception_relation_for_method():
    jdk_exception_data = get_jdk_exception_data()
    for each in jdk_exception_data:
        exception_name = each[0]
        original_method_id = each[1]
        print exception_name, " ", original_method_id
        start_api_id = KnowledgeTableRowMapRecord.get_end_row_id(session, jdk_method_knowledge_table, api_knowledge_table, original_method_id)
        print "start_api_id: ", start_api_id
        original_exception_id = get_class_id_by_exception_name(exception_name)
        if original_exception_id is not None:
            end_api_id = KnowledgeTableRowMapRecord.get_end_row_id(session, jdk_class_knowledge_table, api_knowledge_table, original_exception_id)
            if end_api_id is not None and start_api_id is not None:
                api_relation = APIRelation(start_api_id, end_api_id, APIRelation.RELATION_TYPE_THROW_EXCEPTION)
                print original_method_id, "------------------------------", api_relation
                api_relation.find_or_create(session, autocommit=False)
    session.commit()


if __name__ == "__main__":
    import_jdk_throw_exception_relation_for_method()