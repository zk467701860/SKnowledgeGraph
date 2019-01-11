from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import LibraryEntity, KnowledgeTableRowMapRecord
from db.model_factory import KnowledgeTableFactory

cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()


def create_library_node(row_data):
    library_id = row_data[0]
    library_name = row_data[1]
    library_orgnization = row_data[2]
    library_version = row_data[3]
    library_doc_website = row_data[4]
    library_entity = LibraryEntity(library_name, library_version, library_name, library_doc_website)
    return library_entity, library_id


def import_all_jdk_version():
    jdk_library_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session, "jdk_library")
    library_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session, LibraryEntity.__tablename__)

    # get all-version library
    cur.execute("select * from jdk_library")
    lib_sql_data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(lib_sql_data_list)):
        lib_node, old_id = create_library_node(lib_sql_data_list[i])
        if KnowledgeTableRowMapRecord.exist_import_record(session,jdk_library_knowledge_table,library_knowledge_table,old_id):
            print old_id," has been import to new table"
        else:
            lib_node = lib_node.find_or_create(session, autocommit=False)
            result_tuples.append((lib_node, old_id))
    session.commit()
    for item in result_tuples:
        (lib_node, old_id) = item
        record = KnowledgeTableRowMapRecord(jdk_library_knowledge_table, library_knowledge_table, old_id, lib_node.id)
        record.create(session, autocommit=False)
    session.commit()

    "reading from mysql completed!"


import_all_jdk_version()
cur.close()
