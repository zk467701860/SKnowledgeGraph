from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity
from db.util.code_text_process import clean_html_text
from script.db.jdk_importer.import_jdk_return_value_relation_for_method import \
    construct_qualified_name_by_full_declaration, process_return_type_string


def get_return_value_data(cur):
    sql = 'select full_declaration, return_type, return_string from api_doc.jdk_method where type = "Method"'
    cur.execute(sql)
    return_value_data = cur.fetchall()
    return return_value_data


def import_jdk_return_value(cur, session):
    return_value_data = get_return_value_data(cur)
    for each in return_value_data:
        full_declaration = each[0]
        return_type = each[1]
        return_string = each[2]
        print(return_type)
        return_type = process_return_type_string(return_type)
        qualified_name = construct_qualified_name_by_full_declaration(full_declaration, return_type)
        if qualified_name is not None:
            qualified_name = qualified_name + " (R)"
        else:
            qualified_name = return_type + " (R)"
        return_string = clean_html_text(return_string)
        api_entity = APIEntity(qualified_name, APIEntity.API_TYPE_RETURN_VALUE, return_type, return_string)
        api_entity.find_or_create(session, autocommit=False)
    session.commit()


if __name__ == "__main__":
    session = EngineFactory.create_session()
    cur = ConnectionFactory.create_cursor_for_jdk_importer()
    import_jdk_return_value(cur, session)
