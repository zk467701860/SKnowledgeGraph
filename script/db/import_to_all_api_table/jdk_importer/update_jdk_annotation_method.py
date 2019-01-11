import gc

from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import APIEntity, KnowledgeTableRowMapRecord
from db.model_factory import KnowledgeTableFactory
from script.db.jdk_importer.import_jdk_for_method import generate_qualified_name_for_method
from shared.logger_util import Logger

session = EngineFactory.create_session()
cur = ConnectionFactory.create_cursor_for_jdk_importer()
IMPORT_DATA_SOURCE_TABLE_NAME = "jdk_method"
logger = Logger("import_" + IMPORT_DATA_SOURCE_TABLE_NAME).get_log()
class_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session, name="jdk_class")

jdk_method_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session,
                                                                            name=IMPORT_DATA_SOURCE_TABLE_NAME)
api_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session, name=APIEntity.__tablename__)


def get_data_id_list():
    id_list = []
    print jdk_method_knowledge_table.id, " ", api_knowledge_table.id
    data_list = KnowledgeTableRowMapRecord.get_transformed_table_data(session=session,
                                                                      start_knowledge_table=jdk_method_knowledge_table,
                                                                      end_knowledge_table=api_knowledge_table)
    if data_list is None:
        logger.error("no data in %s", jdk_method_knowledge_table.table_name)
        return None

    for each in data_list:
        # print("end_row_id: " + str(each.end_row_id))
        temp = [each.start_row_id, each.end_row_id]
        id_list.append(temp)
    del data_list
    gc.collect()
    return id_list


def check_and_modify(start_row_id):
    simple_method_name, full_declaration, class_id = get_jdk_method_data_by_id(start_row_id)
    if simple_method_name is not None and full_declaration is not None and class_id is not None:
        # full_declaration = api_entity_alias.full_declaration
        if "(" in full_declaration and ")" in full_declaration and "{" in full_declaration and "}" in full_declaration:
            while "(" in full_declaration and ")" in full_declaration:
                left_bracket_index = full_declaration.find("(")
                right_bracket_index = full_declaration.find(")")
                print full_declaration
                print left_bracket_index, " ", right_bracket_index
                temp = full_declaration[left_bracket_index: right_bracket_index + 1]
                if "{" in temp:
                    full_declaration = full_declaration.replace(temp, '')
                else:
                    break
            qualified_name = generate_qualified_name_for_method(simple_method_name=simple_method_name, api_full_declaration_html=full_declaration, parent_class_id=class_id)
            return qualified_name
    return None


def get_jdk_method_data_by_id(method_id):
    sql = "select name, full_declaration, class_id from api_doc.jdk_method where method_id = " + str(method_id)
    cur.execute(sql)
    jdk_method_data = cur.fetchone()
    if jdk_method_data is not None:
        return jdk_method_data[0], jdk_method_data[1], jdk_method_data[2]
    else:
        return None, None, None


def update_jdk_annotation_method():
    id_list = get_data_id_list()
    for each in id_list:
        start_row_id = each[0]
        end_row_id = each[1]
        qualified_name = check_and_modify(start_row_id)
        if qualified_name is not None:
            print start_row_id, " ", qualified_name
            api_entity = APIEntity.find_by_id(session=session, api_entity_id=end_row_id)
            api_entity.qualified_name = qualified_name
            session.commit()


if __name__ == "__main__":
    update_jdk_annotation_method()