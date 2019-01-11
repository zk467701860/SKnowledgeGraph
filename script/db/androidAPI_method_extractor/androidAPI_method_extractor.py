from db.engine_factory import EngineFactory
from db.model import AndroidAPIMethod, AndroidAPIParameter, AndroidAPIReturnValue, AndroidAPIThrow
from bs4 import BeautifulSoup


def return_value_info(name, url, return_value_text, androidAPI_method_id, type):
    return_value_text = return_value_text.strip()
    androidAPI_return_value = AndroidAPIReturnValue(name, return_value_text, androidAPI_method_id, url, type)
    androidAPI_return_value_list.append(androidAPI_return_value)


def parameter_value_info(name, url, parameter_text, androidAPI_method_id, type):
    parameter_text = parameter_text.strip()
    androidAPI_parameter = AndroidAPIParameter(name, parameter_text, androidAPI_method_id, url, type)
    parameter_value_info_list.append(androidAPI_parameter)


def throws_info(name, url, throw_text, androidAPI_method_id, type):
    throw_text = throw_text.strip()
    androidAPI_throw = AndroidAPIThrow(name, throw_text, androidAPI_method_id, url, type)
    throws_info_list.append(androidAPI_throw)


def commit_one_step():
    try:
        session.commit()
        for androidAPI_return_value in androidAPI_return_value_list:
            androidAPI_return_value.find_or_create(session=session, autocommit=False)

        for parameter_value in parameter_value_info_list:
            parameter_value.find_or_create(session=session, autocommit=False)

        for throw in throws_info_list:
            throw.find_or_create(session=session, autocommit=False)

        session.commit()
    except Exception:
        session.rollback()
        print(Exception.message)


if __name__ == "__main__":

    times = 0
    androidAPI_return_value_list = []
    parameter_value_info_list = []
    throws_info_list = []
    new_androidAPI_method_list = []

    schema_name = 'knowledgeGraph'
    engine = EngineFactory.create_engine_by_schema_name(schema_name)
    session = EngineFactory.create_session(engine=engine, autocommit=False)
    step = 1000

    androidAPI_method_list = session.query(AndroidAPIMethod).all()
    for androidAPI_method in androidAPI_method_list:
        try:
            androidAPI_method_id = androidAPI_method.id
            long_description_label = androidAPI_method.long_description_label
            if long_description_label is not None and long_description_label != '':

                soup = BeautifulSoup(long_description_label, "lxml")
                table_list = soup.find_all(name=['table'])
                if table_list is not None:

                    for table in table_list:
                        table_soup = BeautifulSoup(str(table), "lxml")
                        td_list = table_soup.find_all('td')
                        type_name_div = table_soup.find(attrs={'colspan': 2})
                        td_index = 0
                        while td_index < len(td_list) - 1:
                            code_obj = td_list[td_index].code
                            if code_obj is not None:
                                type_name = code_obj.get_text()
                            elif td_list[td_index].get_text() is not None:
                                type_name = td_list[td_index].get_text()
                            else:
                                type_name = ''
                            url = ''
                            if td_list[td_index].a is not None:
                                url = td_list[td_index].a['href']
                            td_index += 1
                            text = td_list[td_index].get_text()
                            type_obj = td_list[td_index].code
                            if type_obj is not None:
                                type = td_list[td_index].code.get_text()
                                # print(text)
                            else:
                                type = ''
                            if type_name_div.text == 'Parameters':
                                parameter_value_info(type_name, url, text, androidAPI_method_id, type)
                            elif type_name_div.text == 'Returns':
                                return_value_info(type_name, url, text, androidAPI_method_id, type)
                            elif type_name_div.text == 'Throws':
                                throws_info(type_name, url, text, androidAPI_method_id, type)
                        table.decompose()
                    new_long_text = str(soup)
                    androidAPI_method.long_description_remove_table_label = new_long_text
                    new_androidAPI_method_list.append(androidAPI_method)
                if len(parameter_value_info_list) > step:
                    commit_one_step()
                    androidAPI_return_value_list = []
                    parameter_value_info_list = []
                    throws_info_list = []
                    new_androidAPI_method_list = []
                    times += 1
        except Exception:
            print(Exception.message)
    commit_one_step()

print("finish")
