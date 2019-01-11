from bs4 import BeautifulSoup

from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity
from db.model_factory import KnowledgeTableFactory
from db.util.code_text_process import parse_declaration_html_with_full_qualified_type, clean_declaration_html, \
    clean_html_text_with_format
from shared.logger_util import Logger

session = EngineFactory.create_session()

logger = Logger("import_android_method").get_log()
IMPORT_DATA_SOURCE_TABLE_NAME = "androidAPI_method"
class_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session,
                                                                           name="androidAPI_class")

method_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session,
                                                                            name="androidAPI_method")

api_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session, name=APIEntity.__tablename__)


def get_api_entity_id_by_old_class_id(old_class_id):
    return KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                     start_knowledge_table=class_knowledge_table,
                                                     end_knowledge_table=api_knowledge_table,
                                                     start_row_id=old_class_id)


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
        method_split = simple_method_name.split("(",1)
        if "." in method_split[0]:
            new_simple_method_name=method_split[0].split(".")[-1]
            return class_qualified_name + "." + new_simple_method_name+"("+method_split[1]
            # for example :android.app.Notification.DecoratedCustomViewStyle.Notification.DecoratedCustomViewStyle()
        else:
            return class_qualified_name + "." + simple_method_name
    else:
        return None


def generate_qualified_name(api_type, simple_method_name, parent_class_id, api_full_declaration_html):
    if api_type == APIEntity.API_TYPE_METHOD or api_type == APIEntity.API_TYPE_CONSTRUCTOR:
        return generate_qualified_name_for_method(simple_method_name=simple_method_name,
                                                  parent_class_id=parent_class_id,
                                                  api_full_declaration_html=api_full_declaration_html)

    return None


def get_api_type(api_type_string):
    api_type = APIEntity.API_TYPE_UNKNOWN
    if "method" == api_type_string:
        api_type = APIEntity.API_TYPE_METHOD
    if "constructor" == api_type_string:
        api_type = APIEntity.API_TYPE_CONSTRUCTOR

    return api_type


def get_declaration_html_of_method(method_id):
    try:
        cur.execute("select * from method_declaration_link where method_id=" + str(method_id))
        record = cur.fetchone()
        if record is None:
            return None
        html_id = record[0]
        cur.execute("select * from method_declaration_html where id=" + str(html_id))
        declaration_html_record = cur.fetchone()
        declaration_html = declaration_html_record[1]
        soup = BeautifulSoup(declaration_html, "lxml")
        p_list = soup.find_all(name=["p", ])

        for p in p_list:
            p.decompose()

        return str(soup)

    except Exception:
        logger.error("method_id=%d has not declaration_html", method_id)
        return None


def create_method_node(row_data):
    api_method_id = row_data[0]
    api_method_simple_name = row_data[1]
    api_method_first_version = row_data[8]
    api_method_description_html = row_data[2]
    api_method_declaration_html = get_declaration_html_of_method(method_id=api_method_id)

    class_id = row_data[10]

    api_type_string_in_table = row_data[7]
    api_type_string_in_table = api_type_string_in_table.split(" ")[-1]
    api_type = get_api_type(api_type_string_in_table)

    full_declaration = None
    if api_method_declaration_html:
        full_declaration = clean_declaration_html(api_method_declaration_html)
    if full_declaration is None:
        return  None, 0
    short_description = None
    if api_method_description_html:
        short_description = clean_html_text_with_format(api_method_description_html)
        short_description = short_description.strip()
        if not short_description:
            short_description = None

    first_version = None
    if api_method_first_version:
        first_version = api_method_first_version

    if api_type == APIEntity.API_TYPE_UNKNOWN:
        return None, 0

    qualified_name = generate_qualified_name(api_type=api_type,
                                             simple_method_name=api_method_simple_name,
                                             api_full_declaration_html=api_method_declaration_html,
                                             parent_class_id=class_id)
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


def import_all_android_method():
    # get all-version library
    cur.execute("select * from " + IMPORT_DATA_SOURCE_TABLE_NAME)
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        method_node, old_id = create_method_node(data_list[i])
        if method_node is None:
            logger.error(data_list[i])
            logger.error("unkonwn api type")
            continue
        if KnowledgeTableRowMapRecord.exist_import_record(session, method_knowledge_table, api_knowledge_table,
                                                          old_id):
            print old_id, " has been import to new table"
        else:
            method_node = method_node.find_or_create(session, autocommit=False)
            result_tuples.append((method_node, old_id))
    session.commit()
    for item in result_tuples:
        (method_node, old_id) = item
        record = KnowledgeTableRowMapRecord(method_knowledge_table, api_knowledge_table, old_id,
                                            method_node.id)
        record.create(session, autocommit=False)
    session.commit()

    "complete import method"


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_android_importer()
    import_all_android_method()
    cur.close()
