import traceback

from graph_operation import GraphOperation
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor
from skgraph.util.api_name_util import parse_class_name_to_separated_word, \
    parse_method_declaration_to_only_include_formal_parameter_type, \
    parse_method_declaration_to_full_parameter_type_list, parse_method_to_html_link_format, \
    extract_parameter_type_list_from_method_declaration

graphClient = APIGraphAccessor(GraphClient(server_number=1))


class JavaMethodAliasPropertyCreateOperation(GraphOperation):
    name = 'JavaMethodAliasPropertyCreateOperation'

    def operate(self, node):
        api_type = "Method"
        if node["api type"] != "Method":
            return node, node

        if node['name']:
            method_node_id = graphClient.get_id_for_node(node)
            alias_name_list = []
            alias_name_list.append(api_type + " " + node['name'])
            alias_name_list.append(parse_class_name_to_separated_word(node['name']))
            alias_name_list.append(node['name'] + " " + api_type)
            alias_name_list.append(node['name'] + "()")
            alias_name = parse_method_declaration_to_only_include_formal_parameter_type(node['declaration'])

            if alias_name:
                alias_name_list.append(alias_name)

            full_type_alias_name = JavaMethodAliasPropertyCreateOperation.get_full_type_alias_name(node, method_node_id)

            if full_type_alias_name:
                alias_name_list.append(full_type_alias_name)
                node = JavaMethodAliasPropertyCreateOperation.set_api_document_website(
                    full_type_alias_name=full_type_alias_name, method_node_id=method_node_id,
                    node=node)
            node["alias"] = list(set(alias_name_list))

        return node, node

    @staticmethod
    def get_full_type_alias_name(node, method_node_id):
        parameter_node_list = graphClient.get_parameter_nodes_of_method(method_node_id)
        parameter_type_and_full_name_map = {}

        for parameter_node in parameter_node_list:
            try:
                full_type_str = parameter_node["formal parameter type full name"]
                simple_type_str = parameter_node["formal parameter type"]
                if not simple_type_str:
                    continue
                if full_type_str:
                    parameter_type_and_full_name_map[simple_type_str] = full_type_str
                else:
                    parameter_type_and_full_name_map[simple_type_str] = simple_type_str
            except Exception:
                traceback.print_exc()

        method_declaration = node['declaration']
        if parameter_node_list is []:
            type_list = extract_parameter_type_list_from_method_declaration(method_declaration)
            if type_list is []:
                node["full type method name"] = node["name"] + "()"
                return node["name"] + "()"
            else:
                # todo used the link api interface in here
                # try to link without a good parameter node
                for parameter_simple_type in type_list:
                    parameter_type_class_node = graphClient.find_one_by_name_property("java class",
                                                                                      parameter_simple_type)
                    if parameter_type_class_node is None:
                        parameter_type_class_node = graphClient.find_one_by_alias_name_property(
                            "java class",
                            parameter_simple_type)

                    if parameter_type_class_node is not None:
                        if parameter_type_class_node["name"]:
                            parameter_type_and_full_name_map[parameter_simple_type] = parameter_type_class_node["name"]
                        else:
                            parameter_type_and_full_name_map[parameter_simple_type] = parameter_simple_type

        try:

            full_type_alias_name = parse_method_declaration_to_full_parameter_type_list(method_declaration,
                                                                                        parameter_type_and_full_name_map)

            node["full type method name"] = full_type_alias_name
            return full_type_alias_name
        except Exception:
            traceback.print_exc()
            return None

    @staticmethod
    def set_api_document_website(full_type_alias_name, method_node_id, node):
        try:
            class_node = graphClient.get_parent_class_node_for_method_node(method_node_id)
            if class_node is not None:
                class_document_website = class_node["api document website"]
                if class_document_website:
                    if class_document_website.startswith("https://developer.android.com/reference/"):
                        method_website = class_document_website + "#" + parse_method_to_html_link_format(
                            full_type_alias_name, "android api")
                    else:
                        method_website = class_document_website + "#" + parse_method_to_html_link_format(
                            full_type_alias_name)
                    node["api document website"] = method_website
            return node
        except Exception:
            traceback.print_exc()
            return node
