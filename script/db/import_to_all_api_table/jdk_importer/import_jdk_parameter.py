from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity
from db.util.code_text_process import clean_html_text


def read_jdk_parameter_data(cur):
    sql = "select name, type_class, type_string, description from api_doc.jdk_parameter"
    cur.execute(sql)
    jdk_parameter_data = cur.fetchall()
    return jdk_parameter_data


def import_jdk_parameter(cur, session):
    jdk_parameter_data = read_jdk_parameter_data(cur)
    for each in jdk_parameter_data:
        print(each)
        name = each[0]
        type_class = each[1]
        type_string = each[2]
        description = each[3]
        qualified_class_name = get_qualified_class_name(type_class, cur)
        print(qualified_class_name)
        if qualified_class_name is not None:
            qualified_name = qualified_class_name[0] + " " + name
        else:
            qualified_name = type_string + " " + name
        full_declaration = type_string + " " + name
        print(qualified_name)
        print(full_declaration)
        description = clean_html_text(description)
        api_entity = APIEntity(qualified_name, APIEntity.API_TYPE_PARAMETER, full_declaration, description)
        api_entity.find_or_create(session, autocommit=False)
    session.commit()


def get_qualified_class_name(type_class, cur):
    if type_class is not None:
        sql = "select name from api_doc.jdk_class where class_id = " + str(type_class)
        cur.execute(sql)
        class_name = cur.fetchone()
        return class_name


# if __name__ == "__main__":
#     cur = ConnectionFactory.create_cursor_for_jdk_importer()
#     session = EngineFactory.create_session()
#     import_jdk_parameter(cur, session)
