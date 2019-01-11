from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIRelation, KnowledgeTableColumnMapRecord, APIBelongToLibraryRelation
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_belong_to_relation_for_jdk_package").get_log()

cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()
jdk_package_knowledge_table = KnowledgeTableFactory.get_jdk_package_table(session)

jdk_library_knowledge_table = KnowledgeTableFactory.get_jdk_library_table(session)
library_entity_knowledge_table = KnowledgeTableFactory.get_library_entity_table(session)

api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)

api_belong_to_table = KnowledgeTableFactory.get_api_belong_to_library_relation_table(session)

COMMIT_STEP = 5000


def is_imported(row_id):
    if KnowledgeTableColumnMapRecord.exist_import_record(session, jdk_package_knowledge_table, api_belong_to_table,
                                                         row_id,
                                                         "library_id"):
        return True
    else:
        return False


def create_package_belong_to_relation(old_package_id, old_library_id):
    if old_library_id is None:
        logger.error("no old_library_id for %d", old_package_id)
        return None
    new_library_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                      start_knowledge_table=jdk_library_knowledge_table,
                                                                      end_knowledge_table=library_entity_knowledge_table,
                                                                      start_row_id=old_library_id)
    if new_library_entity_id is None:
        logger.error("no new_library_entity_id for %d", old_library_id)
        return None
    new_package_api_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                          start_knowledge_table=jdk_package_knowledge_table,
                                                                          end_knowledge_table=api_knowledge_table,
                                                                          start_row_id=old_package_id)
    if new_package_api_entity_id is None:
        logger.error("no new_package_api_entity_id for %d", old_package_id)
        return None
    relation = APIBelongToLibraryRelation(api_id=new_package_api_entity_id, library_id=new_library_entity_id)

    logger.info("%d belong to %d", new_package_api_entity_id, new_library_entity_id)
    return relation


def import_all_belong_to_relation():
    cur.execute("select package_id,library_id from jdk_package")
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        old_package_id = data_list[i][0]
        old_library_id = data_list[i][1]

        if is_imported(old_package_id):
            logger.info("%d has been import to new table", old_package_id)
            continue
        relation = create_package_belong_to_relation(old_package_id=old_package_id, old_library_id=old_library_id)

        if relation is None:
            logger.info("None Relation")
            logger.info(data_list[i])
            continue

        relation = relation.find_or_create(session, autocommit=False)
        result_tuples.append((relation, old_package_id))
        if len(result_tuples) > COMMIT_STEP:
            commit_to_server(result_tuples)
            result_tuples = []
    commit_to_server(result_tuples)
    logger.info("import belong to relation completed!")


def commit_to_server(result_tuples):
    print "success=", len(result_tuples)
    session.commit()
    for item in result_tuples:
        (relation, old_id) = item
        record = KnowledgeTableColumnMapRecord(jdk_package_knowledge_table, api_belong_to_table, old_id,
                                               relation.id, "library_id")
        record.create(session, autocommit=False)
    session.commit()


import_all_belong_to_relation()

cur.close()
