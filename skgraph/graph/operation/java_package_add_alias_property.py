from graph_operation import GraphOperation


class JavaPackageAliasPropertyCreateOperation(GraphOperation):
    name = 'JavaPackageAliasPropertyCreateOperation'

    def operate(self, node):
        node_name = node['name']
        api_type = "Package"
        if node["api type"]:
            api_type = node["api type"]
        else:
            node["api type"] = "Package"

        if node_name:
            alias_name_list = []
            alias_name_list.append("package " + node_name)
            separated_name = node_name.replace(".", " ")
            alias_name_list.append("package " + separated_name.split(" ")[-1])
            alias_name_list.append(separated_name.split(" ")[-1] + " package")
            alias_name_list.append(node_name + " package")
            alias_name_list.append("package " + separated_name)
            alias_name_list.append(separated_name)
            node["alias"] = list(set(alias_name_list))

        return node, node
