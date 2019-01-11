from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity
from db.model_factory import KnowledgeTableFactory
from db.util.code_text_process import clean_html_text
from shared.logger_util import Logger

session = EngineFactory.create_session()

logger = Logger("import_android_class").get_log()
IMPORT_DATA_SOURCE_TABLE_NAME = "androidAPI_class"
package_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session, name="androidAPI_package")
class_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session,
                                                                           name=IMPORT_DATA_SOURCE_TABLE_NAME)
api_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session=session, name=APIEntity.__tablename__)


def get_package_full_name_by_old_package_id(package_id):
    return KnowledgeTableRowMapRecord.get_end_row_id(session=session,
                                                     start_knowledge_table=package_knowledge_table,
                                                     end_knowledge_table=api_knowledge_table,
                                                     start_row_id=package_id)


def get_qualified_name_of_package(package_id):
    api_entity_id = get_package_full_name_by_old_package_id(package_id=package_id)
    api_entity = APIEntity.find_by_id(session, api_entity_id)
    if api_entity:
        return api_entity.qualified_name
    else:
        return None


def generate_qualified_name_for_class(simple_class_name, class_package_id):
    if not class_package_id or not simple_class_name:
        return None
    package_qualified_name = get_qualified_name_of_package(package_id=class_package_id)
    if package_qualified_name:
        return package_qualified_name + "." + simple_class_name
    else:
        return None


def get_api_type_from_full_declaration(full_declaration):
    if not full_declaration:
        return APIEntity.API_TYPE_UNKNOWN

    api_type = APIEntity.API_TYPE_UNKNOWN
    if " class " in full_declaration:
        api_type = APIEntity.API_TYPE_CLASS
    if " interface " in full_declaration:
        api_type = APIEntity.API_TYPE_INTERFACE
    if "Error " in full_declaration:
        api_type = APIEntity.API_TYPE_ERROR
    if "Enum" in full_declaration and " enum " in full_declaration:
        api_type = APIEntity.API_TYPE_ENUM_CLASS
    if "Exception " in full_declaration:
        api_type = APIEntity.API_TYPE_EXCEPTION
    if " @interface " in full_declaration:
        api_type = APIEntity.API_TYPE_ANNOTATION

    return api_type


def create_class_node(row_data):
    old_id = row_data[0]
    # no full package name, only the class name, etc. "android.view.Button" has simple name "Button"

    simple_class_name = row_data[1]

    short_description_html = row_data[2]
    first_version = row_data[6]
    full_declaration = row_data[7]
    package_id = row_data[9]

    short_description = None
    if short_description_html:
        short_description = clean_html_text(short_description_html)
        short_description = short_description.strip()
        if not short_description:
            short_description = None

    qualified_name = generate_qualified_name_for_class(simple_class_name=simple_class_name, class_package_id=package_id)
    api_type = get_api_type_from_full_declaration(full_declaration)
    print "type=", api_type, " form ", full_declaration

    if api_type == APIEntity.API_TYPE_UNKNOWN:
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

    return api_entity, old_id


def import_all_class():
    # get all-version library
    cur.execute("select * from " + IMPORT_DATA_SOURCE_TABLE_NAME)
    data_list = cur.fetchall()
    result_tuples = []
    for i in range(0, len(data_list)):
        class_node, old_id = create_class_node(data_list[i])
        if class_node is None:
            logger.error(data_list[i])
            logger.error("unkonwn api type")
            continue
        if KnowledgeTableRowMapRecord.exist_import_record(session, class_knowledge_table, api_knowledge_table,
                                                          old_id):
            print old_id, " has been import to new table"
        else:
            class_node = class_node.find_or_create(session, autocommit=False)
            result_tuples.append((class_node, old_id))
    session.commit()
    for item in result_tuples:
        (class_node, old_id) = item
        record = KnowledgeTableRowMapRecord(class_knowledge_table, api_knowledge_table, old_id,
                                            class_node.id)
        record.create(session, autocommit=False)
    session.commit()

    "reading from mysql completed!"


cur = ConnectionFactory.create_cursor_for_android_importer()
import_all_class()
cur.close()
