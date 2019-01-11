# coding=utf-8
import sys
from urllib import unquote

from db.cursor_factory import ConnectionFactory
from script.db.jdk_importer.import_jdk_return_value_relation_for_method import process_return_type_string

reload(sys)
sys.setdefaultencoding("UTF-8")


def read_jdk_method_data(cur):
    sql = 'select method_id, name, full_declaration, return_type from api_doc.jdk_method where type = "Method"'
    cur.execute(sql)
    jdk_method_data = cur.fetchall()
    return jdk_method_data


def update_jdk_method_data(cur, method_id, return_value):
    sql = 'update api_doc.jdk_method set return_type = "' + return_value + '" where method_id = ' + str(method_id)
    cur.execute(sql)


def clean_jdk_method(cur):
    jdk_method_data = read_jdk_method_data(cur)
    index = 0
    for each in jdk_method_data:
        method_id = each[0]
        name = each[1]
        full_declaration = each[2]
        return_type = each[3]
        name = str(" ") + name
        return_value_string = full_declaration[:full_declaration.find(name)]
        return_type = process_return_type_string(return_type)
        if return_type.strip() not in return_value_string:
            print("-----------------------------------------")
            print(return_type)
            print(return_value_string)
            index += 1
            return_value_string = return_value_string.replace("<pre>", "").replace('<a href="../../../java/lang/Deprecated.html" title="annotation in java.lang">@Deprecated</a>', '')
            if "<" not in return_value_string:
                return_value_list = return_value_string.split(" ")
                return_value = return_value_list[-1]
            else:
                temp = return_value_string[return_value_string.find(">") + 1:]
                return_value = temp[:temp.find("<")]
            return_value = return_value.replace("[]", "")
            print(return_value)
            update_jdk_method_data(cur, method_id, return_value)
    conn.commit()
    print(index)


if __name__ == "__main__":
    cur, conn = ConnectionFactory.create_cursor_and_conn()
    clean_jdk_method(cur)