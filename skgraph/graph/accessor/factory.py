import json
import os

from py2neo import Graph, Node


class GraphFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_from_default_config(server_number=1):
        file_dir = os.path.split(os.path.realpath(__file__))[0]
        file_name = 'config.json'
        full_path = os.path.join(file_dir, file_name)
        return GraphFactory.create_from_config_file(full_path=full_path, server_number=server_number)

    @staticmethod
    def create_from_config_file(full_path, server_number=1):
        if os.path.isfile(full_path) is False:
            raise Exception(full_path + "is not exist!\nGraph Client can not init!")

        with open(full_path, 'r') as f:
            config = json.load(f)
            if server_number == 0:
                config = config['debugServer']
            else:
                server_name = "produceServer" + str(server_number)
                if server_name not in config.keys():
                    return None, None
                config = config[server_name]

            return Graph(host=config['host'],
                         http_port=config['http_port'],
                         https_port=config['https_port'],
                         bolt_port=config['bolt_port'],
                         user=config['user'],
                         password=config['password']), config


class NodeBuilder:
    '''
    a builder for Node
    '''

    def __init__(self):
        self.labels = []
        self.property_dict = {}

    def add_labels(self, *labels):
        '''
        add labels for Node
        :param labels: all labels need to be added
        :return: a NodeBuilder object
        '''
        self.labels.extend(labels)
        self.labels = list(set(self.labels))

        return self

    def add_label(self, label):
        '''
        add label for Node
        :param label: label, string
        :return: a NodeBuilder object
        '''
        if label not in self.labels:
            self.labels.append(label)
        return self

    def add_property(self, **property_dict):
        self.property_dict = dict(self.property_dict, **property_dict)
        return self

    def add_one_property(self, property_name, property_value):
        if property_value is None or property_value is "":
            return self
        self.property_dict[property_name] = property_value
        return self

    def add_label_concept(self):
        return self.add_labels('concept')

    def add_label_property(self):
        return self.add_labels('property')

    def add_sentence_label(self):
        return self.add_labels('sentence')

    def add_domain_entity_label(self):
        return self.add_labels('domain entity')

    def add_label_wikidata(self):
        return self.add_labels('wikidata')

    def add_label_wikipedia(self):
        return self.add_labels('wikipedia')

    def add_label_wall(self):
        return self.add_labels('wall')

    def add_entity_label(self):
        return self.add_labels('entity')

    def add_relation_label(self):
        return self.add_labels('relation')

    def add_api_label(self):
        return self.add_labels('api')

    def add_as_alias(self):
        '''
        add the node as a aliases node
        :return: the node builder
        '''
        return self.add_label("alias")

    def build(self):
        node = Node(*self.labels)
        for key in self.property_dict:
            node[key] = self.property_dict[key]
        return node
