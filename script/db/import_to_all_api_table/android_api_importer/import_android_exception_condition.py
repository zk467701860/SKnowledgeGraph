from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity


def read_android_exception_data(cur):
    sql = 'SELECT name, throw_text, throw_url FROM knowledgeGraph.androidAPI_throw where name != "" and throw_url != "" and name like "%Exception%";'
    cur.execute(sql)
    android_exception_data = cur.fetchall()
    return android_exception_data


def import_android_exception_condition(cur, session):
    exception_data = read_android_exception_data(cur)
    for each in exception_data:
        exception_name = each[0]
        exception_text = each[1].replace("\n", '').replace("           ", '').replace("     ", '').replace("  ", '').replace("   ", '')
        exception_url = each[2]
        qualified_name_list = exception_url.replace("https://developer.android.google.cn/reference/", '').replace(".html", "").split("/")
        qualified_name = ""
        for i in range(0, len(qualified_name_list)):
            if i == 0:
                qualified_name += qualified_name_list[i]
            else:
                qualified_name += ("." + qualified_name_list[i])
        qualified_name += " (E)"
        print(qualified_name)
        api_entity = APIEntity(qualified_name, APIEntity.API_TYPE_EXCEPTION_CONDITION, exception_name, exception_text)
        api_entity.find_or_create(session, autocommit=False)
    session.commit()


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_android_importer()
    session = EngineFactory.create_session()
    import_android_exception_condition(cur, session)
