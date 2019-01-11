from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity
from db.util.code_text_process import clean_html_text


def read_android_return_value_data(cur):
    sql = 'select name, return_value_text, return_value_url from knowledgeGraph.androidAPI_return_value'
    cur.execute(sql)
    return_value_data = cur.fetchall()
    return return_value_data


def import_android_return_value(cur, session):
    return_value_data = read_android_return_value_data(cur)
    for each in return_value_data:
        print(each)
        return_value_name = each[0]
        return_value_text = clean_html_text(each[1])
        return_value_url = each[2]
        # print(return_value_name)
        # print(return_value_text)
        # print(return_value_url)
        qualified_name = ""
        if return_value_url != "":
            qualified_name_list = return_value_url.replace("https://developer.android.google.cn/reference/", "").replace(".html", "").split("/")
            for i in range(0, len(qualified_name_list)):
                if i == 0:
                    qualified_name += qualified_name_list[i]
                else:
                    qualified_name += ("." + qualified_name_list[i])
        else:
            qualified_name = return_value_name
        qualified_name = qualified_name + " (R)"
        print(qualified_name)
        api_entity = APIEntity(qualified_name, APIEntity.API_TYPE_RETURN_VALUE, return_value_name, return_value_text)
        # print(api_entity)
        api_entity.find_or_create(session, autocommit=False)
    session.commit()


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_android_importer()
    session = EngineFactory.create_session()
    import_android_return_value(cur, session)