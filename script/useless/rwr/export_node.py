# -*- coding:utf8 -*-
import codecs
import sys

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient

reload(sys)
sys.setdefaultencoding('utf8')


class NodeExportor:
    def __init__(self, client, max_id):
        self.client = client
        self.max_id = max_id

    def export_node(self):
        output_file = codecs.open('node.txt', 'w', 'utf-8')
        id = 1
        while id <= self.max_id:
            print id
            node_list = self.client.get_node_in_scope(id, id + 999)
            for node in node_list:
                name = self.get_name_from_property(node)
                if name != '':
                    if type(name) == list:
                        name = name[0]
                    for label in node.labels():
                        if label != 'wall':
                            replace_label = label.replace('\t', ' ')
                            replace_label = replace_label.replace('\n', ' ')
                            input_str = name + '\thas label\t' + replace_label + '\n'
                            output_file.write(input_str)
                    for keys in node:
                        if keys != 'lastrevid' and keys != 'modified':
                            need_keys = 1
                            if (keys.find('aliases_') != -1 and keys != 'aliases_en') or (
                                    keys.find('descriptions_') != -1 and keys != 'descriptions_en') or (
                                    keys.find('labels_') != -1 and keys != 'labels_en'):
                                need_keys = 0
                            if need_keys == 1:
                                if type(node[keys]) != list:
                                    replace_property = node[keys].replace('\t', ' ')
                                    replace_property = replace_property.replace('\n', ' ')
                                    input_str = name + '\t' + keys + '\t' + replace_property + '\n'
                                    output_file.write(input_str)
                                else:
                                    for i in node[keys]:
                                        replace_property = i.replace('\t', ' ')
                                        replace_property = replace_property.replace('\n', ' ')
                                        input_str = name + '\t' + keys + '\t' + replace_property + '\n'
                                        output_file.write(input_str)
            id += 1000
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
    exporter = NodeExportor(client, max_id)
    exporter.export_node()
