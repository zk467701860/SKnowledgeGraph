from graph_operation import GraphOperation
from skgraph.util.api_name_util import parse_class_name_to_separated_word


class JavaClassAliasPropertyCreateOperation(GraphOperation):
    name = 'JavaClassAliasPropertyCreateOperation'

    def operate(self, node):
        api_type = "Class"
        if node["api type"]:
            api_type = node["api type"]
        else:
            node["api type"] = "Class"
        if node['name']:
            alias_name_list = []
            alias_name_list.append(api_type + " " + node['name'])

            seperated_name = node['name'].replace(".", " ")
            seperated_name_words = seperated_name.split(" ")
            alias_name_list.append(seperated_name_words[-1])
            alias_name_list.append(parse_class_name_to_separated_word(seperated_name_words[-1]))
            alias_name_list.append(seperated_name_words[-1] + " " + api_type)
            alias_name_list.append(api_type + " " + seperated_name_words[-1])

            alias_name_list.append(api_type + " " + seperated_name)
            alias_name_list.append(seperated_name)
            alias_name_list.append(seperated_name + " " + api_type)

            node["alias"] = list(set(alias_name_list))
        return node, node
