import codecs
import json
import os


class PropertyCleanUtil:

    def __init__(self):
        self.property_name_dict = {}
        self.file_path = os.path.join(".", 'property_name_map.txt')

    def load(self, property_id_name_map_file_path='.', property_id_name_map_file_name='property_name_map.txt'):
        self.file_path = os.path.join(property_id_name_map_file_path, property_id_name_map_file_name)
        if os.path.isfile(self.file_path):
            self.property_name_dict = json.load(codecs.open(self.file_path, 'r', 'utf-8'))

    def init_by_outside_source(self, property_dict):
        self.property_name_dict = property_dict

    def get_property_name(self, property_id):
        if property_id in self.property_name_dict:
            return self.property_name_dict[property_id]
        else:
            return None

    def update_property_dict(self, **property_name_dict):
        self.property_name_dict = dict(self.property_name_dict, **property_name_dict)
        self.save()

    def save(self):
        json.dump(self.property_name_dict, codecs.open(self.file_path, 'w', 'utf-8'))

    def filter_not_in_property_name_list(self, name_list):
        result = []
        for name in name_list:
            if name not in self.property_name_dict:
                result.append(name)
        return result

    def exist(self, property_id):
        if property_id in self.property_name_dict:
            return True
        else:
            return False

    def add(self, property_id, label):
        self.property_name_dict[property_id] = label

    def replace_property_id(self, property_dict, property_id_list):
        for property_id in property_id_list:
            property_name = self.get_property_name(property_id)
            if property_name:
                value = property_dict.pop(property_id)
                property_dict[property_name] = value
        return property_dict

    def translate_property_list(self, property_id_list):
        property_name_list = []
        for id in property_id_list:
            name = self.get_property_name(id)
            if name:
                property_name_list.append(name)
        return property_name_list
