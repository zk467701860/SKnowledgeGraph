from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity
from db.util.code_text_process import clean_html_text


def read_exception_condition_data(cur):
    sql = "select name, description from api_doc.jdk_exception"
    cur.execute(sql)
    exception_condition_data = cur.fetchall()
    return exception_condition_data


def get_qualified_name_by_simple_name(name, cur):
    if name is not None:
        sql = 'select name from api_doc.jdk_class where class_name = "' + name + '"'
        cur.execute(sql)
        qualified_name_data = cur.fetchone()
        if qualified_name_data is not None:
            return qualified_name_data[0]
    return None


def import_jdk_exception_condition(cur, session):
    exception_condition_data = read_exception_condition_data(cur)
    for each in exception_condition_data:
        name = each[0]
        description = each[1]
        qualified_name = get_qualified_name_by_simple_name(name, cur)
        if qualified_name is not None:
            qualified_name = qualified_name + ' (E)'
        else:
            qualified_name = name + ' (E)'
        print(qualified_name)
        description = clean_html_text(description)
        api_entity = APIEntity(qualified_name, APIEntity.API_TYPE_EXCEPTION_CONDITION, name, description)
        api_entity.find_or_create(session, autocommit=False)
    session.commit()


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_jdk_importer()
    session = EngineFactory.create_session()
    import_jdk_exception_condition(cur, session)