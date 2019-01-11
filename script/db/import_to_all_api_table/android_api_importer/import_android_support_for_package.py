from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity
from db.model_factory import KnowledgeTableFactory

cur = ConnectionFactory.create_cursor_for_android_importer()
session = EngineFactory.create_session()


def create_package_node(row_data):
    package_id = row_data[0]
    package_full_name = row_data[1]
    package_short_description = row_data[3]

    package_first_version = row_data[4]

    package_entity = APIEntity(qualified_name=package_full_name, api_type=APIEntity.API_TYPE_PACKAGE,
                               full_declaration=package_full_name, added_in_version=package_first_version,
                               short_description=package_short_description)
    return package_entity, package_id


def import_all_android_package():
    jdk_package_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session,
                                                                                     "androidAPI_support_package")
    api_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session, APIEntity.__tablename__)

    # get all-version library
    cur.execute("select * from androidAPI_support_package")
    package_data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(package_data_list)):
        package_node, old_id = create_package_node(package_data_list[i])
        if KnowledgeTableRowMapRecord.exist_import_record(session, jdk_package_knowledge_table, api_knowledge_table,
                                                          old_id):
            print old_id, " has been import to new table"
        else:
            package_node = package_node.find_or_create(session, autocommit=False)
            result_tuples.append((package_node, old_id))
    session.commit()
    for item in result_tuples:
        (package_node, old_id) = item
        record = KnowledgeTableRowMapRecord(jdk_package_knowledge_table, api_knowledge_table, old_id,
                                            package_node.id)
        record.create(session, autocommit=False)
    session.commit()

    "reading from mysql completed!"


import_all_android_package()
cur.close()
