from extractor import WikiDataEntityIDStorage
from graph_operation import GraphOperation


class FixWallNodeLabelErrorOperation(GraphOperation):
    name = 'FixWallNodeLabelErrorOperation'
    item_id_list = []

    def __init__(self):
        GraphOperation.__init__(self)
        wikiDataEntityIDStorage = WikiDataEntityIDStorage()
        wikiDataEntityIDStorage.load()
        self.item_id_list = wikiDataEntityIDStorage.get_accept_id_list()
        print 'len=', len(self.item_id_list)

    def operate(self, node):
        if node['wd_item_id'] and node['wd_item_id'] in self.item_id_list:
            node.remove_label('wall')
        return node, node
