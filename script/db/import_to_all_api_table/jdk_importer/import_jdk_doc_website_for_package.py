from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIDocumentWebsite, KnowledgeTableColumnMapRecord
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_doc_website_for_jdk_package").get_log()

cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()
jdk_package_knowledge_table = KnowledgeTableFactory.get_jdk_package_table(session)
api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)

api_document_website_table = KnowledgeTableFactory.get_api_document_website_table(session)


def create_doc_website_relation(old_package_id, doc_website):
    if doc_website is None:
        logger.error("no doc_website for %d", old_package_id)
        return None
    new_package_api_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                          start_knowledge_table=jdk_package_knowledge_table,
                                                                          end_knowledge_table=api_knowledge_table,
                                                                          start_row_id=old_package_id)
    if new_package_api_entity_id is None:
        logger.error("no new_package_api_entity_id for %d", old_package_id)
        return None

    relation = APIDocumentWebsite(new_package_api_entity_id, doc_website)

    logger.info("API %d :  %s", new_package_api_entity_id, doc_website)
    return relation


def import_all_package_class_doc_website_relation():
    # get all-version library
    cur.execute("select package_id,doc_website from jdk_package")
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        old_package_id = data_list[i][0]
        relation = create_doc_website_relation(old_package_id=old_package_id, doc_website=data_list[i][1])

        if relation is None:
            logger.info("None Relation")
            logger.info(data_list[i])
            continue

        relation = relation.find_or_create(session, autocommit=False)
        result_tuples.append((relation, old_package_id))

    session.commit()
    for item in result_tuples:
        (relation, old_id) = item
        record = KnowledgeTableColumnMapRecord(jdk_package_knowledge_table, api_document_website_table, old_id,
                                               relation.id, "doc_website")
        record.create(session, autocommit=False)
    session.commit()
    logger.info("import all completed!")


import_all_package_class_doc_website_relation()

cur.close()
