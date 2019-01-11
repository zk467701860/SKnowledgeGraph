from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity, APIRelation
from db.model_factory import KnowledgeTableFactory
from shared.logger_util import Logger

logger = Logger("import_return_value_relation_for_jdk_method").get_log()
cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()
jdk_method_knowledge_table = KnowledgeTableFactory.get_jdk_method_table(session)
api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)


def get_return_value_data():
    sql = 'select method_id, full_declaration, return_type from api_doc.jdk_method where type = "Method"'
    cur.execute(sql)
    return_value_data = cur.fetchall()
    return return_value_data


def extract_angle_bracket_body_from_full_declaration(full_declaration):
    result = []
    if full_declaration is not None:
        if "<" in full_declaration and ">" in full_declaration:
            while "<" in full_declaration and ">" in full_declaration:
                left_bracket_index = full_declaration.find("<")
                right_bracket_index = full_declaration.find(">")
                angle_bracket_body = full_declaration[left_bracket_index: right_bracket_index + 1]
                result.append(angle_bracket_body)
                full_declaration = full_declaration.replace(angle_bracket_body, "")
    return result


def process_return_type_string(return_type):
    if "<" in return_type:
        temp_index = return_type.find("<")
        return_type = return_type[:temp_index]
    if "[" in return_type:
        return_type = return_type.replace("[", "")
    if "]" in return_type:
        return_type = return_type.replace("]", "")
    if "protected" in return_type:
        return_type = return_type.replace("protected", "")
    if "abstract" in return_type:
        return_type = return_type.replace("abstract", "")
    if "default" in return_type:
        return_type = return_type.replace("default", "")
    return return_type.strip()


def construct_qualified_name_by_href(href):
    result = ""
    if href is not None:
        left_index = href.find("href=") + 6
        right_index = href.find(".html")
        qualified_str = href[left_index: right_index]
        qualified_list = qualified_str.split("/")
        for each in qualified_list:
            if each == "..":
                continue
            else:
                result += (each + ".")
        if result[-1] == ".":
            result = result[:-1]
    return result


def construct_qualified_name_by_full_declaration(full_declaration, return_type):
    if return_type is not None:
        processed_return_type = process_return_type_string(return_type)
        if full_declaration is not None:
            # print "----------------------------------------"
            # print processed_return_type
            # print full_declaration
            target = ""
            angle_bracket_list = extract_angle_bracket_body_from_full_declaration(full_declaration)
            for each in angle_bracket_list:
                if processed_return_type in each:
                    target = each
                    break
            # print target
            qualified_name = construct_qualified_name_by_href(target)
            # print qualified_name
            if qualified_name is not None and qualified_name is not "":
                return qualified_name
    return None


def import_jdk_relation_value_relation_for_method():
    return_value_data = get_return_value_data()
    for each in return_value_data:
        original_method_id = each[0]
        full_declaration = each[1]
        return_type = each[2]
        start_api_id = KnowledgeTableRowMapRecord.get_end_row_id(session, jdk_method_knowledge_table, api_knowledge_table, original_method_id)
        qualified_name = construct_qualified_name_by_full_declaration(full_declaration, return_type)
        if start_api_id is not None and qualified_name is not None:
            print "-------------------------------------"
            print "start_api_id: ", start_api_id, ", qualified_name: ", qualified_name
            api_entity = APIEntity.find_by_qualifier(session, qualified_name)
            if api_entity is not None:
                end_api_id = api_entity.id
                print api_entity, " ", end_api_id
                api_relation = APIRelation(start_api_id, end_api_id, APIRelation.RELATION_TYPE_RETURN_VALUE)
                print api_relation
                api_relation.find_or_create(session, autocommit=False)
    session.commit()


if __name__ == "__main__":
    import_jdk_relation_value_relation_for_method()