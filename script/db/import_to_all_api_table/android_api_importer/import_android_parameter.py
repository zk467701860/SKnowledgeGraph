from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity


def read_parameter_data(cur):
    sql = 'select id, method_name, full_declaration from knowledgeGraph.androidAPI_method where type like "%method%"'
    cur.execute(sql)
    parameter_data = cur.fetchall()
    return parameter_data


def get_qualified_type_list(method_id, method_name, cur):
    sql1 = 'select method_declaration_html_id from knowledgeGraph.method_declaration_link where method_id = ' + str(method_id)
    cur.execute(sql1)
    declaration_data = cur.fetchone()
    if declaration_data is not None:
        declaration_id = declaration_data[0]
        sql2 = 'select html from knowledgeGraph.method_declaration_html where id = ' + str(declaration_id)
        cur.execute(sql2)
        method_html_data = cur.fetchone()
        if method_html_data is not None:
            method_html = method_html_data[0]
            # print(method_html)
            # print(method_name)
            left_index = method_html.find("#"+method_name) + len(method_name) + 1
            # print(left_index)
            temp = method_html[left_index + 1:]
            # print(temp)
            right_index = temp.find(")")
            qualified_type_str = temp[0: right_index]
            print(qualified_type_str)
            while "&lt;" in qualified_type_str and "&gt;" in qualified_type_str:
                bracket = qualified_type_str[qualified_type_str.find("&lt;"): qualified_type_str.find("&gt;") + 4]
                if "&lt;" in bracket[1:]:
                    temp = bracket[1:]
                    bracket = temp[temp.find("&lt;"):]
                qualified_type_str = qualified_type_str.replace(bracket, "")
            qualified_type_list = qualified_type_str.split(", ")
            return qualified_type_list
    return None


def get_simple_parameter_list(full_declaration):
    if "(" in full_declaration and ")" in full_declaration:
        left_index = full_declaration.find("(")
        right_index = full_declaration.find(")")
        parameter_str = full_declaration[left_index + 1: right_index]
        print(parameter_str)
        if parameter_str != "":
            while "<" in parameter_str and ">" in parameter_str:
                bracket = parameter_str[parameter_str.find("<"): parameter_str.find(">") + 1]
                if "<" in bracket[1:]:
                    temp = bracket[1:]
                    bracket = temp[temp.find("<"):]
                parameter_str = parameter_str.replace(bracket, "")
            if "," in parameter_str:
                parameter_list = parameter_str.split(",")
            else:
                parameter_list = [parameter_str]
            return parameter_list
    return None


def import_android_parameter(cur, session):
    android_parameter_data = read_parameter_data(cur)
    for each in android_parameter_data:
        # print(each)
        method_id = each[0]
        method_name = each[1]
        qualified_type_list = get_qualified_type_list(method_id, method_name, cur)

        full_declaration = each[2]
        simple_parameter_list = get_simple_parameter_list(full_declaration)
        if qualified_type_list is not None and simple_parameter_list is not None and len(qualified_type_list) == len(simple_parameter_list):
            for i in range(0, len(qualified_type_list)):
                parameter_var = simple_parameter_list[i].split(" ")[-1]
                qualified_type_list[i] += (" " + parameter_var)
                qualified_type_list[i] = qualified_type_list[i].replace("[]", "").replace("...", "").strip()
                simple_parameter_list[i] = simple_parameter_list[i].replace("[]", "").replace("...", "").strip()

                if qualified_type_list[i] != "" and simple_parameter_list[i] != "":
                    print(qualified_type_list[i])
                    print(simple_parameter_list[i])
                    api_entity = APIEntity(qualified_type_list[i], APIEntity.API_TYPE_PARAMETER, simple_parameter_list[i])
                    api_entity.find_or_create(session, autocommit=False)
    session.commit()


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_android_importer()
    session = EngineFactory.create_session()
    import_android_parameter(cur, session)
