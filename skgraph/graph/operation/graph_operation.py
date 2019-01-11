class GraphOperation:
    name = 'GraphOperation'

    def __init__(self):
        pass

    def operate(self, node):
        '''
        operate in one node
        :param node: the operate node
        :return: the first return value is the node updated,
        the second return value is the all related graph for node.include the relation,node newly created
        '''
        return node,node


class TestOperation(GraphOperation):
    name = 'TestOperation'

    def operate(self, node):
        print "operate node:", node
        print node['xxx']
        return node,node


class CreateNameForWikiDataNodeOperation(GraphOperation):
    name = 'CreateNameForWikiDataNodeOperation'

    def operate(self, node):
        if node['labels_en']:
            node['name'] = node['labels_en']
        return node,node


class CreateNameForAPIClassNodeOperation(GraphOperation):
    name = 'CreateNameForAPIClassNodeOperation'

    def operate(self, node):
        if node['api_class_name']:
            node['name'] = node['api_class_name']
        return node,node


class CreateNameForAPIMethodNodeOperation(GraphOperation):
    name = 'CreateNameForAPIMethodNodeOperation'

    def operate(self, node):
        if node['api_method_name']:
            node['name'] = node['api_method_name']
            node['method name']=node['api_method_name']
            del node['api_method_name']
        return node,node


class CreateNameForAPIFieldNodeOperation(GraphOperation):
    name = 'CreateNameForAPIFieldNodeOperation'

    def operate(self, node):
        if node['api_field_name']:
            node['name'] = node['api_field_name']
        return node,node
