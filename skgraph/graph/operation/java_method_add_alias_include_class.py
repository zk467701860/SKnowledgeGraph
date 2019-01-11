
from skgraph.graph.accessor.graph_accessor import GraphClient
from graph_operation import GraphOperation
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor

graphClient = APIGraphAccessor(GraphClient(server_number=5))


class JavaFieldAliasPropertyIncludeClassNameCreateOperation(GraphOperation):
    name = 'JavaFieldAliasPropertyIncludeClassNameCreateOperation'

    def operate(self, node):
        api_type = "Method"
        if node["api type"] != "Method":
            return node, node
        alias_name_list = node["alias"]
        if alias_name_list is None or alias_name_list is []:
            alias_name_list = []
        if node['name']:
            method_node_id = graphClient.get_id_for_node(node)
            class_node = graphClient.get_parent_class_node_for_method_node(method_node_id)

            alias_name = class_node["name"] + "." + node["method name"] + "()"
            # aliasGraphClient.create_alias_node_for_name(alias_name, method_node_id)
            alias_name_list.append(alias_name)

            if node["full type method name"]:
                alias_name = class_node["name"] + "." + node["full type method name"]
                # aliasGraphClient.create_alias_node_for_name(alias_name, method_node_id)
                alias_name_list.append(alias_name)

            node["alias"] = list(set(alias_name_list))
            graphClient.push(node)
        return node, node
