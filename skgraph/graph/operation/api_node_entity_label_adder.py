from graph_operation import GraphOperation


class APINodeEntityLabelAdderOperation(GraphOperation):
    name = 'APINodeEntityLabelAdderOperation'

    def operate(self, node):
        node.add_label("entity")
        return node, node
