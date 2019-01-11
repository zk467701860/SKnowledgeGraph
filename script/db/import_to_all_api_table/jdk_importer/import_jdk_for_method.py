from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity, parse_api_type_string_to_api_type_constant
from db.model_factory import KnowledgeTableFactory
from db.util.code_text_process import clean_declaration_html, clean_html_text_with_format, \
    parse_declaration_html_with_full_qualified_type
from shared.logger_util import Logger

session = EngineFactory.create_session()

IMPORT_DATA_SOURCE_TABLE_NAME = "jdk_method"
logger = Logger("import_" + IMPORT_DATA_SOURCE_TABLE_NAME).get_log()
class_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session, name="jdk_class")

method_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session,
                                                                            name=IMPORT_DATA_SOURCE_TABLE_NAME)
api_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session, name=APIEntity.__tablename__)


def get_api_entity_id_by_old_class_id(old_class_id):
    return KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                     start_knowledge_table=class_knowledge_table,
                                                     end_knowledge_table=api_knowledge_table,
                                                     start_row_id=old_class_id)


def get_qualified_name_of_class(old_class_id):
    api_entity_id = get_api_entity_id_by_old_class_id(old_class_id=old_class_id)
    api_entity = APIEntity.find_by_id(session, api_entity_id)
    if api_entity:
        return api_entity.qualified_name
    else:
        return None


def generate_qualified_name_for_method(simple_method_name, api_full_declaration_html, parent_class_id):
    simple_method_name = generate_simple_method_name_with_qualified_type(simple_method_name, api_full_declaration_html)
    class_qualified_name = get_qualified_name_of_class(old_class_id=parent_class_id)
    if simple_method_name and class_qualified_name:
        return class_qualified_name + "." + simple_method_name
    else:
        return None


def get_api_type_from_full_declaration(full_declaration, api_type_string_in_table):
    api_type = APIEntity.type_string_to_api_type_constant(api_type_string_in_table)
    if api_type != APIEntity.API_TYPE_UNKNOWN:
        return api_type

    if not full_declaration:
        return APIEntity.API_TYPE_UNKNOWN

    api_type = APIEntity.API_TYPE_UNKNOWN

    return api_type


def generate_qualified_name_for_nested_class(simple_class_name, parent_class_id):
    if not parent_class_id or not simple_class_name:
        return None
    class_qualified_name = get_qualified_name_of_class(parent_class_id)
    if class_qualified_name:
        if "." not in simple_class_name:
            return class_qualified_name + "." + simple_class_name
        else:
            names = simple_class_name.split(".", 1)
            nested_class_name = names[1]
            parent_class_name = names[0]
            if parent_class_name in class_qualified_name:
                return class_qualified_name + "." + nested_class_name
            else:
                return class_qualified_name + "." + simple_class_name
    else:
        return None


def generate_qualified_name_for_field(simple_class_name, parent_class_id):
    if not parent_class_id or not simple_class_name:
        return None
    class_qualified_name = get_qualified_name_of_class(parent_class_id)
    if class_qualified_name:
        return class_qualified_name + "." + simple_class_name
    else:
        return None


def generate_simple_method_name_with_qualified_type(method_simple_name, api_method_declaration_html):
    if "(" in api_method_declaration_html and ")" in api_method_declaration_html and "{" in api_method_declaration_html and "}" in api_method_declaration_html:
        while "(" in api_method_declaration_html and ")" in api_method_declaration_html:
            left_bracket_index = api_method_declaration_html.find("(")
            right_bracket_index = api_method_declaration_html.find(")")
            temp = api_method_declaration_html[left_bracket_index: right_bracket_index + 1]
            if "{" in temp:
                api_method_declaration_html = api_method_declaration_html.replace(temp, '')
            else:
                break

    full_declaration = parse_declaration_html_with_full_qualified_type(api_method_declaration_html)
    parameters_string = full_declaration.split("(", 1)[1].split(")", 1)[0].strip()

    parameter_types = []
    parameters = parameters_string.split(",")

    for declaration in parameters:
        t = declaration.rstrip(declaration.split(" ")[-1]).strip()
        parameter_types.append(t)
    return method_simple_name + "(" + ",".join(parameter_types) + ")"


def generate_qualified_name(api_type, row_data):
    if api_type == APIEntity.API_TYPE_CLASS:
        return generate_qualified_name_for_nested_class(simple_class_name=row_data[2], parent_class_id=row_data[11])
    if api_type == APIEntity.API_TYPE_FIELD or api_type == APIEntity.API_TYPE_ENUM_CONSTANTS:
        return generate_qualified_name_for_field(simple_class_name=row_data[2], parent_class_id=row_data[11])
    if api_type == APIEntity.API_TYPE_METHOD or api_type == APIEntity.API_TYPE_CONSTRUCTOR:
        return generate_qualified_name_for_method(simple_method_name=row_data[2], parent_class_id=row_data[11],
                                                  api_full_declaration_html=row_data[3])

    return None


def create_method_node(row_data):
    api_method_id = row_data[0]
    api_type_string_in_table = row_data[1]
    api_method_simple_name = row_data[2]
    api_method_declaration_html = row_data[3]
    api_method_description_html = row_data[6]
    api_method_first_version = row_data[7]

    full_declaration = None
    if api_method_declaration_html:
        full_declaration = clean_declaration_html(api_method_declaration_html)

    short_description = None
    if api_method_description_html:
        short_description = clean_html_text_with_format(api_method_description_html)
        short_description = short_description.strip()
        if not short_description:
            short_description = None

    first_version = None
    if api_method_first_version:
        first_version = api_method_first_version

    api_type = get_api_type_from_full_declaration(full_declaration, api_type_string_in_table)

    if api_type == APIEntity.API_TYPE_UNKNOWN:
        return None, 0

    qualified_name = generate_qualified_name(api_type=api_type, row_data=row_data)
    if qualified_name is None:
        logger.error("qualified_name is None")
        return None, 0

    api_entity = APIEntity(qualified_name=qualified_name, api_type=api_type,
                           full_declaration=full_declaration, added_in_version=first_version,
                           short_description=short_description)

    logger.info(row_data)
    logger.info(qualified_name)
    logger.info(api_type)
    logger.info(full_declaration)
    logger.info(first_version)
    logger.info(short_description)

    return api_entity, api_method_id


def import_all_method():
    # get all-version method
    cur.execute("select * from " + IMPORT_DATA_SOURCE_TABLE_NAME)
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        row_data = data_list[i]
        try:
            import_one_row(result_tuples, row_data)
        except Exception:
            logger.error(row_data)
            logger.error("import one row fail")
    session.commit()
    for item in result_tuples:
        (method_node, old_id) = item
        record = KnowledgeTableRowMapRecord(method_knowledge_table, api_knowledge_table, old_id,
                                            method_node.id)
        record.create(session, autocommit=False)
    session.commit()

    logger.info("import from mysql completed!")


def is_imported(row_data):
    old_id = row_data[0]
    if KnowledgeTableRowMapRecord.exist_import_record(session, method_knowledge_table, api_knowledge_table,
                                                      old_id):
        return True
    else:
        return False


def import_one_row(result_tuples, row_data):
    old_id = row_data[0]
    if is_imported(row_data):
        logger.info("%d has been import to new table", old_id)
        return

    method_node, old_id = create_method_node(row_data)
    if method_node is None:
        logger.error(row_data)
        logger.error("unkonwn api type")
        return

    method_node = method_node.find_or_create(session, autocommit=False)
    result_tuples.append((method_node, old_id))


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_jdk_importer()
    import_all_method()
    cur.close()
