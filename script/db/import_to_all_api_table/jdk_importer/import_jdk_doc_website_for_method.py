import gc

from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity, APIDocumentWebsite
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_doc_website_for_jdk_method").get_log()

cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()
jdk_method_knowledge_table = KnowledgeTableFactory.get_jdk_method_table(session)
api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)


def create_doc_website_relation(method_name, full_declaration, qualified_name, class_website):
    # print class_website
    if "http://docs.oracle.com/javase/7/docs/api/" in class_website:
        return None
    if full_declaration:
        if method_name[0] == "_":
            method_name = "Z:Z" + method_name
        if "(" in qualified_name and ")" in qualified_name:
            left_bracket_index = qualified_name.find("(")
            right_bracket_index = qualified_name.find(")")
            param_str = qualified_name[left_bracket_index + 1: right_bracket_index]
            if "," in param_str:
                param_list = param_str.split(",")
            else:
                param_list = [param_str]

            url = class_website + "#" + method_name + "-"
            for each in param_list:
                if "<" in each and ">" in each:
                    left_index = each.find("<")
                    right_index = each.find(">")
                    paradigm = each[left_index: right_index + 1]
                    each = each.replace(paradigm, "")
                type_value = each.strip().split(" ")
                print type_value
                class_type = type_value[0]
                print class_type
                if "[]" in class_type:
                    temp_full_class_name = class_type.replace("[]", '')
                    # full_class_name = get_full_class_name(temp_full_class_name) + ":A"
                    full_class_name = temp_full_class_name + ":A"
                else:
                    full_class_name = class_type

                url += (full_class_name + "-")
            print url
        else:
            url = class_website + "#" + method_name
            print url
    else:
        last_slant_index = find_last(class_website, "/")
        url = class_website[:last_slant_index + 1] + method_name + ".html"
        print url
    return url


def get_property_from_api_entity(end_row_id):
    api_entity_data = APIEntity.find_by_id(session=session, api_entity_id=end_row_id)
    if api_entity_data is not None:
        return api_entity_data.qualified_name, api_entity_data.full_declaration
    else:
        return None, None


def get_full_class_name(class_name):
    sql = 'select name from api_doc.jdk_class where class_name = binary "' + class_name + '"'
    cur.execute(sql)
    data = cur.fetchone()
    if data is None:
        return class_name
    else:
        return data[0]


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


def import_all_jdk_method_doc_website_relation():
    # with open("url.txt", 'w') as f:
    id_list = get_data_id_list()
    for each in id_list:
        print "start_row_id: ", each[0], ", end_row_id: ", each[1]
        sql = "select * from api_doc.jdk_method where method_id = " + str(each[0])
        cur.execute(sql)
        method_data = cur.fetchone()
        method_name, class_website = get_properties_from_jdk_method(method_data)
        qualified_name, full_declaration = get_property_from_api_entity(each[1])
        url = create_doc_website_relation(method_name, full_declaration, qualified_name, class_website)
        if url is not None:
            api_document_website = APIDocumentWebsite(each[1], url)
            api_document_website.find_or_create(session, autocommit=False)
            # f.write(url)
            # f.write("\n")
    session.commit()


def get_properties_from_jdk_method(method_data):
    if method_data:
        print method_data
        method_name = method_data[2]
        class_id = method_data[11]
        full_declaration = method_data[14]
        print method_name, " ", class_id, " ", full_declaration
        sql = "select doc_website from api_doc.jdk_class where class_id = " + str(class_id)
        cur.execute(sql)
        class_website_data = cur.fetchone()
        if class_website_data:
            class_website = class_website_data[0]
            print class_website
            return method_name, class_website
    return None


def find_last(string, str):
    last_position = -1
    while True:
        position = string.find(str, last_position + 1)
        if position == -1:
            return last_position
        last_position = position


if __name__ == "__main__":
    import_all_jdk_method_doc_website_relation()
    cur.close()
