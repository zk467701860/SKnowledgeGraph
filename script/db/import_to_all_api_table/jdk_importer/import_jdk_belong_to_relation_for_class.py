from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIRelation, KnowledgeTableColumnMapRecord
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_belong_to_relation_for_jdk_class").get_log()

cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()
jdk_package_knowledge_table = KnowledgeTableFactory.get_jdk_package_table(session)
jdk_class_knowledge_table = KnowledgeTableFactory.get_jdk_class_table(session)
api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)

api_relation_table = KnowledgeTableFactory.get_api_relation_table(session)


def create_class_belong_to_relation(old_class_id, old_package_id):
    if old_package_id is None:
        logger.error("no old_package_id for %d", old_class_id)
        return None
    new_class_api_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                        start_knowledge_table=jdk_class_knowledge_table,
                                                                        end_knowledge_table=api_knowledge_table,
                                                                        start_row_id=old_class_id)
    if new_class_api_entity_id is None:
        logger.error("no new_class_api_entity_id for %d", old_class_id)
        return None
    new_package_api_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                          start_knowledge_table=jdk_package_knowledge_table,
                                                                          end_knowledge_table=api_knowledge_table,
                                                                          start_row_id=old_package_id)
    if new_package_api_entity_id is None:
        logger.error("no new_package_api_entity_id for %d", old_package_id)
        return None
    relation = APIRelation(new_class_api_entity_id, new_package_api_entity_id, APIRelation.RELATION_TYPE_BELONG_TO)

    logger.info("%d belong to %d", new_class_api_entity_id, new_package_api_entity_id)
    return relation


def create_class_extends_relation(old_class_id, old_extended_class_id):
    if old_extended_class_id is None:
        logger.error("no old_extends_parent_class_id for %d", old_class_id)
        return None
    new_class_api_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                        start_knowledge_table=jdk_class_knowledge_table,
                                                                        end_knowledge_table=api_knowledge_table,
                                                                        start_row_id=old_class_id)
    if new_class_api_entity_id is None:
        logger.error("no new_class_api_entity_id for %d", old_class_id)
        return None
    new_extended_class_api_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                                 start_knowledge_table=jdk_class_knowledge_table,
                                                                                 end_knowledge_table=api_knowledge_table,
                                                                                 start_row_id=old_extended_class_id)
    if new_extended_class_api_entity_id is None:
        logger.error("no new_extended_class_api_entity_id for %d", old_extended_class_id)
        return None
    relation = APIRelation(new_class_api_entity_id, new_extended_class_api_entity_id, APIRelation.RELATION_TYPE_EXTENDS)

    logger.info("%d extends to %d", new_class_api_entity_id, new_extended_class_api_entity_id)
    return relation


def import_all_jdk_class_belong_to_relation():
    # get all-version library
    cur.execute("select class_id,package_id from jdk_class")
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        old_class_id = data_list[i][0]
        relation = create_class_belong_to_relation(old_class_id=old_class_id, old_package_id=data_list[i][1])

        if relation is None:
            logger.info("None Relation")
            logger.info(data_list[i])
            continue

        relation = relation.find_or_create(session, autocommit=False)
        result_tuples.append((relation, old_class_id))
    session.commit()
    for item in result_tuples:
        (relation, old_id) = item
        record = KnowledgeTableColumnMapRecord(jdk_class_knowledge_table, api_relation_table, old_id,
                                               relation.id, "package_id")
        record.create(session, autocommit=False)
    session.commit()
    logger.info("import class belong to relation completed!")


def import_all_jdk_class_extends_relation():
    # get all-version library
    cur.execute("select class_id,extend_class from jdk_class")
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        relation = create_class_extends_relation(old_class_id=data_list[i][0],
                                                 old_extended_class_id=data_list[i][1])

        if relation is None:
            logger.info("None Relation")
            logger.info(data_list[i])
            continue

        relation = relation.find_or_create(session, autocommit=False)
    session.commit()
    for item in result_tuples:
        (relation, old_id) = item
        record = KnowledgeTableColumnMapRecord(jdk_class_knowledge_table, api_relation_table, old_id,
                                               relation.id, "extend_class")
        record.create(session, autocommit=False)
    session.commit()
    logger.info("import class extends relation completed!")


import_all_jdk_class_belong_to_relation()
import_all_jdk_class_extends_relation()

cur.close()
