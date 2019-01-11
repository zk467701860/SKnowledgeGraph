from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIRelation, KnowledgeTableColumnMapRecord
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_belong_to_relation_for_jdk_method").get_log()

cur = ConnectionFactory.create_cursor_for_android_importer()
session = EngineFactory.create_session()
android_method_knowledge_table = KnowledgeTableFactory.get_android_method_table(session)

android_class_knowledge_table = KnowledgeTableFactory.get_android_class_table(session)
api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)

api_relation_table = KnowledgeTableFactory.get_api_relation_table(session)

COMMIT_STEP = 5000


def is_imported(row_id):
    if KnowledgeTableColumnMapRecord.exist_import_record(session, android_method_knowledge_table, api_relation_table,
                                                         row_id,
                                                         "class_id"):
        return True
    else:
        return False


def create_method_belong_to_relation(old_method_id, old_class_id):
    logger.info("old_method_id=%d old_class_id=%d", old_method_id, old_class_id)

    if old_class_id is None:
        logger.error("no old_class_id for %d", old_method_id)
        return None
    new_method_api_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                  start_knowledge_table=android_method_knowledge_table,
                                                                  end_knowledge_table=api_knowledge_table,
                                                                  start_row_id=old_method_id)
    if new_method_api_id is None:
        logger.error("no new_method_api_id for %d", old_method_id)
        return None

    new_class_api_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                        start_knowledge_table=android_class_knowledge_table,
                                                                        end_knowledge_table=api_knowledge_table,
                                                                        start_row_id=old_class_id)
    if new_class_api_entity_id is None:
        logger.error("no new_class_api_entity_id for %d", old_class_id)
        return None
    relation = APIRelation(new_method_api_id, new_class_api_entity_id, APIRelation.RELATION_TYPE_BELONG_TO)

    logger.info("%d belong to %d", new_method_api_id, new_class_api_entity_id)
    return relation


def import_all_android_method_belong_to_relation():
    # get all-version library
    #todo ,fix the select statement
    cur.execute("select id,class_id from androidAPI_method")
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        old_method_id = data_list[i][0]
        old_class_id = data_list[i][1]

        if is_imported(old_method_id):
            logger.info("%d has been import to new table", old_method_id)
            continue
        relation = create_method_belong_to_relation(old_method_id=old_method_id, old_class_id=old_class_id)

        if relation is None:
            logger.info("None Relation")
            logger.info(data_list[i])
            continue

        relation = relation.find_or_create(session, autocommit=False)
        result_tuples.append((relation, old_method_id))

        if len(result_tuples) > COMMIT_STEP:
            commit_to_server(result_tuples)
            result_tuples = []
    commit_to_server(result_tuples)
    logger.info("import method belong to relation completed!")


def commit_to_server(result_tuples):
    print "success=", len(result_tuples)
    session.commit()
    for item in result_tuples:
        (relation, old_id) = item
        record = KnowledgeTableColumnMapRecord(android_method_knowledge_table, api_relation_table, old_id,
                                               relation.id, "class_id")
        record.create(session, autocommit=False)
    session.commit()


if __name__ == "__main__":
    import_all_android_method_belong_to_relation()
    cur.close()
