import re
import traceback

pattern = re.compile(r"([0-9A-Z])")
method_parameter_list_pattern = re.compile(r"\([\s\S]*\)")
method_name_pattern = re.compile(r"[ ]*[A-Za-z0-9_]+[ ]*\(")


def get_formal_parameter_type_from_method_declaration(method_declaration):
    '''
    :param method_declaration: etc."void showStatus(String status)"
    :return:
    '''
    try:
        formal_parameter_list_str = re.findall(method_parameter_list_pattern, method_declaration)
        if formal_parameter_list_str:
            formal_parameter_list_str = formal_parameter_list_str[0].strip()[1:-1].strip()
            if formal_parameter_list_str == "":
                return "()"
            else:
                type_list = []
                for formal_parameter_str in formal_parameter_list_str.split(","):
                    type_list.append(" ".join(formal_parameter_str.strip().split(" ")[:-1]))
                return ",".join(type_list)

    except Exception:
        print Exception
        return None


def parse_class_name_to_separated_word(class_name):
    '''
    parse a class name to separated word,or parse a method name to seperated word, not "()" include
    :param class_name: the class name, et. "android.view.WindowManager,org.xmlpull.v1.V1XmlHTTPPullParser"
    :return: the separated name Window Manager
    '''

    if "." in class_name:
        class_name = class_name.split(".")[-1]
    if "_" in class_name:
        return " ".join(class_name.split("_"))

    class_name = re.sub(pattern, r" \1", class_name)

    result = []
    words = class_name.split(" ")
    last_conbined_word = ""
    for word in words:
        if len(word) == 0:
            continue
        if len(word) > 1:
            if last_conbined_word:
                result.append(last_conbined_word)
                last_conbined_word = ""
            result.append(word)
        else:
            last_conbined_word = last_conbined_word + word
    if last_conbined_word:
        result.append(last_conbined_word)
    return " ".join(result)


def parse_method_declaration_to_full_parameter_type_list(method_declaration, type_name_to_full_type_map):
    '''
    :param method_declaration: etc."void showStatus(String status)"->showStatus(java.lang.String)
    :return:
    '''
    try:
        method_name = re.findall(method_name_pattern, method_declaration)[0][:-1].strip()
        formal_parameter_list_str = re.findall(method_parameter_list_pattern, method_declaration)
        if formal_parameter_list_str:
            formal_parameter_list_str = formal_parameter_list_str[0].strip()[1:-1].strip()
            if formal_parameter_list_str == "":
                return method_name + "()"
            else:

                type_list = []

                for formal_parameter_str in formal_parameter_list_str.split(","):
                    type_list.append(" ".join(formal_parameter_str.strip().split(" ")[:-1]))

                if len(type_name_to_full_type_map.keys()) <= 0:
                    return method_name + "(" + ",".join(type_list) + ")"
                full_type_list = []

                for type_str in type_list:
                    if type_str:
                        if type_str in type_name_to_full_type_map.keys():
                            full_type_list.append(type_name_to_full_type_map[type_str])
                        else:
                            full_type_list.append(type_str)

                return method_name + "(" + ",".join(full_type_list) + ")"

    except Exception:
        traceback.print_exc()
        print "error=method_declaration:"
        print method_declaration
        return None


def extract_parameter_type_list_from_method_declaration(method_declaration):
    '''
        :param method_declaration: etc."void showStatus(String status)"->showStatus(java.lang.String)
        :return:
    '''
    try:
        method_name = re.findall(method_name_pattern, method_declaration)[0][:-1].strip()
        formal_parameter_list_str = re.findall(method_parameter_list_pattern, method_declaration)
        if formal_parameter_list_str:
            formal_parameter_list_str = formal_parameter_list_str[0].strip()[1:-1].strip()
            if formal_parameter_list_str == "":
                return []
            else:
                type_list = []

                for formal_parameter_str in formal_parameter_list_str.split(","):
                    type_list.append(" ".join(formal_parameter_str.strip().split(" ")[:-1]))
                return type_list

    except Exception:
        traceback.print_exc()
        print "error=method_declaration:"
        print method_declaration
        return []


def parse_method_declaration_to_only_include_formal_parameter_type(method_declaration):
    '''
    :param method_declaration: etc."void showStatus(String status)"
    :return:
    '''
    try:
        method_name = re.findall(method_name_pattern, method_declaration)[0][:-1].strip()
        formal_parameter_list_str = re.findall(method_parameter_list_pattern, method_declaration)
        if formal_parameter_list_str:
            formal_parameter_list_str = formal_parameter_list_str[0].strip()[1:-1].strip()
            if formal_parameter_list_str == "":
                return method_name + "()"
            else:
                type_list = []
                for formal_parameter_str in formal_parameter_list_str.split(","):
                    type_list.append(" ".join(formal_parameter_str.strip().split(" ")[:-1]))
                return method_name + "(" + ",".join(type_list) + ")"

    except Exception:
        print Exception
        return None


def parse_method_to_html_link_format(method_declaration, format_type="jdk 1.8"):
    if format_type == "jdk 1.8":
        method_declaration = method_declaration.replace("(", "-").replace(")", "-").replace(",", "-").replace("[]",
                                                                                                              ":A")
        return method_declaration
    else:
        return method_declaration

# full_type_method_name = parse_method_declaration_to_full_parameter_type_list(
#     "getMatrix(double[])", {"URL": "view.URL", "String": "java.lang.String"})
#
# print parse_method_to_html_link_format_for(full_type_method_name)
