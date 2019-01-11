# -*- coding:utf8 -*-
import codecs
import sys

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient

reload(sys)
sys.setdefaultencoding('utf8')


class RelationExportor:
    def __init__(self, client, max_id):
        self.client = client
        self.max_id = max_id

    def export_relation(self):
        output_file = codecs.open('relation.txt', 'w', 'utf-8')
        id = 1
        while id <= self.max_id:
            print id
            start_node = self.client.find_node_by_id(id)
            if start_node != None:
                start_name = self.get_name_from_property(start_node)
                if start_name != '':
                    relation_node_list = self.client.find_outward_relation_by__id(id)
                    for relation_node in relation_node_list:
                        relation_name = ''
                        for i in range(0, 2):
                            if i == 0:
                                relation_name = relation_node[i].type()
                            else:
                                end_node = relation_node[i]
                        end_name = self.get_name_from_property(end_node)
                        if end_name != '':
                            if type(start_name) == list:
                                start_name = start_name[0]
                            if type(end_name) == list:
                                end_name = end_name[0]
                            input_str = start_name + '\t' + relation_name + '\t' + end_name + '\n'
                            output_file.write(input_str)
            id += 1
        output_file.close()

    def get_name_from_property(self, property):
        if 'name' in property:
            return property['name']
        elif 'labels_en' in property:
            return property['labels_en']
        else:
            for keys in property:
                if 'labels_' in keys:
                    return property[keys]
        return ''


if __name__ == '__main__':
    client = DefaultGraphAccessor(GraphClient(server_number=1))
    max_id = client.get_max_id_for_node()
    exporter = RelationExportor(client, max_id)
    exporter.export_relation()
