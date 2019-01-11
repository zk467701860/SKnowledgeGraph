from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIBelongToLibraryRelation
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_belong_to_relation_for_android_package").get_log()

cur = ConnectionFactory.create_cursor_for_android_importer()
session = EngineFactory.create_session()
android_package_knowledge_table = KnowledgeTableFactory.get_android_package_table(session)

library_entity_knowledge_table = KnowledgeTableFactory.get_library_entity_table(session)

api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)

api_belong_to_table = KnowledgeTableFactory.get_api_belong_to_library_relation_table(session)

COMMIT_STEP = 5000


def create_package_belong_to_relation(old_package_id, new_library_entity_id):
    if new_library_entity_id is None:
        logger.error("no new_library_entity_id for %d", new_library_entity_id)
        return None
    new_package_api_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                                          start_knowledge_table=android_package_knowledge_table,
                                                                          end_knowledge_table=api_knowledge_table,
                                                                          start_row_id=old_package_id)
    if new_package_api_entity_id is None:
        logger.error("no new_package_api_entity_id for %d", old_package_id)
        return None
    relation = APIBelongToLibraryRelation(api_id=new_package_api_entity_id, library_id=new_library_entity_id)

    logger.info("%d belong to %d", new_package_api_entity_id, new_library_entity_id)
    return relation


def import_all_belong_to_relation():
    new_library_entity_id = 1
    cur.execute("select id from androidAPI_package")
    data_list = cur.fetchall()
    for i in range(0, len(data_list)):
        old_package_id = data_list[i][0]

        relation = create_package_belong_to_relation(old_package_id=old_package_id,
                                                     new_library_entity_id=new_library_entity_id)

        if relation is None:
            logger.info("None Relation")
            logger.info(data_list[i])
            continue

        relation = relation.find_or_create(session, autocommit=False)
    session.commit()
    logger.info("import belong to relation completed!")


if __name__ == "__main__":
    import_all_belong_to_relation()

    cur.close()
