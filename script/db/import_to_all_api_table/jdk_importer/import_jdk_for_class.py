from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity
from db.model_factory import KnowledgeTableFactory

cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()


def create_class_node(row_data):
    old_id = row_data[0]
    qualified_name = row_data[1]
    short_description = row_data[3]
    first_version = row_data[6]
    api_type_string = row_data[8]

    api_type = APIEntity.type_string_to_api_type_constant(api_type_string)

    if api_type == APIEntity.API_TYPE_UNKNOWN:
        print "---------------xxxxxxx ", api_type, api_type_string, row_data
        return None, 0
    api_entity = APIEntity(qualified_name=qualified_name, api_type=api_type,
                           full_declaration=None, added_in_version=first_version,
                           short_description=short_description)
    return api_entity, old_id


def import_all_jdk_class():
    jdk_class_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session, "jdk_class")
    api_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session, APIEntity.__tablename__)

    # get all-version library
    cur.execute("select * from jdk_class")
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        class_node, old_id = create_class_node(data_list[i])
        if class_node is None:
            print "unkonwn api type", data_list[i]
            continue
        if KnowledgeTableRowMapRecord.exist_import_record(session, jdk_class_knowledge_table, api_knowledge_table,
                                                          old_id):
            print old_id, " has been import to new table"
        else:
            class_node = class_node.find_or_create(session, autocommit=False)
            result_tuples.append((class_node, old_id))
    session.commit()
    for item in result_tuples:
        (class_node, old_id) = item
        record = KnowledgeTableRowMapRecord(jdk_class_knowledge_table, api_knowledge_table, old_id,
                                            class_node.id)
        record.create(session, autocommit=False)
    session.commit()

    "reading from mysql completed!"


import_all_jdk_class()
cur.close()
