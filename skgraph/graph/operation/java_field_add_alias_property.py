import traceback

from graph_operation import GraphOperation
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor
from skgraph.util.api_name_util import parse_class_name_to_separated_word

graphClient = APIGraphAccessor(GraphClient(server_number=1))


class JavaFieldAliasPropertyCreateOperation(GraphOperation):
    name = 'JavaFieldAliasPropertyCreateOperation'

    def operate(self, node):
        api_type = "Field"
        if node["api type"]:
            api_type = node["api type"]
        if node['name']:
            field_node_id = graphClient.get_id_for_node(node)

            alias_name_list = []
            alias_name_list.append(parse_class_name_to_separated_word(node['name']))
            alias_name_list.append(api_type + " " + node['name'])
            alias_name_list.append("constant " + " " + node['name'])

            node["alias"] = list(set(alias_name_list))
            node = JavaFieldAliasPropertyCreateOperation.set_api_document_website(field_node_id, node)
        return node, node

    @staticmethod
    def set_api_document_website(field_node_id, node):
        try:
            class_node = graphClient.get_parent_class_node_for_field_node(field_node_id)
            if class_node is not None:
                class_document_website = class_node["api document website"]
                if class_document_website:
                    method_website = class_document_website + "#" + node['name']
                    node["api document website"] = method_website
            return node
        except Exception:
            traceback.print_exc()
            return node
