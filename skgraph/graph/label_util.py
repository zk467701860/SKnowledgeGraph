import json
import os


class PrivateLabel:
    def __init__(self, name, description, priority, public_name, type, is_public):
        self.name = name
        self.description = description
        self.priority = priority
        self.public_name = public_name
        self.type = type
        self.is_public = is_public
        self.public_label_object = None

    def has_public_label(self):
        return self.is_public and self.public_label_object != None

    def set_public_label_object(self, public_label_object):
        self.public_label_object = public_label_object

    def get_public_label_object(self):
        return self.public_label_object

    def __eq__(self, other):
        if isinstance(other, str):
            if self.name == other:
                return True
            else:
                return False
        if isinstance(other, PrivateLabel):
            return self.name == other.name
        return False

    def __repr__(self):
        return '<PrivateLabel: name=%r  description=%r>' % (self.name, self.description)

    def __hash__(self):
        return hash((self.name,))


class PublicLabel:
    def __init__(self, name, description, priority):
        self.name = name
        self.description = description
        self.priority = priority

    def __eq__(self, other):
        if isinstance(other, str):
            if self.name == other:
                return True
            else:
                return False
        if isinstance(other, PublicLabel):
            return self.name == other.name
        return False

    def __repr__(self):
        return '<PublicLabel: name=%r  description=%r>' % (self.name, self.description)

    def __hash__(self):
        return hash((self.name,))


class LabelUtil:

    def __init__(self):
        self.labels_json = None
        self.all_data = None
        self.private_labels_object_list = []
        self.public_labels_object_list = []
        self.private_property_names = []
        self.init_label_data()

    def init_label_data(self, labels_json_file="new_labels.json"):
        file_dir = os.path.split(os.path.realpath(__file__))[0]
        full_path = os.path.join(file_dir, labels_json_file)

        if os.path.isfile(full_path) is False:
            raise Exception(full_path + "is not exist!")

        with open(full_path, 'r') as f:
            labels_json = json.load(f)
            self.__init_private_label_object(labels_json["labels"])
            self.__init_public_label_object(labels_json["public_labels"])
            self.private_property_names = labels_json["private_property_names"]
            self.__init_public_label_object_for_private_label_object()

            self.DEFAULT_PUBLIC_LABEL_NAME = labels_json["default_public_name"]

    def __init_private_label_object(self, labels_json):
        self.private_labels_object_list = []
        for team_json in labels_json:
            label = PrivateLabel(**team_json)
            self.private_labels_object_list.append(label)

    def __init_public_label_object(self, labels_json):
        self.public_labels_object_list = []
        for team_json in labels_json:
            label = PublicLabel(**team_json)
            self.public_labels_object_list.append(label)

    def __init_public_label_object_for_private_label_object(self):
        for private_label in self.private_labels_object_list:
            for public_label in self.public_labels_object_list:
                if private_label.is_public and private_label.public_name == public_label.name:
                    private_label.set_public_label_object(public_label)

    def get_private_property_names(self):
        return self.private_property_names

    def get_private_label_object_by_name(self, name):
        for label in self.private_labels_object_list:
            if label.name == name:
                return label
        return None

    def get_public_label_object_by_name(self, name):
        for public_label in self.public_labels_object_list:
            if public_label.name == name:
                return public_label
        return None

    def filter_labels_set_to_public_label_object_list(self, private_labels_set):
        public_label_object_set = set([])
        for private_label_name in private_labels_set:
            private_label_object = self.get_private_label_object_by_name(private_label_name)
            if private_label_object is None:
                continue
            public_label_object = private_label_object.get_public_label_object()
            if public_label_object is None:
                continue
            public_label_object_set.add(public_label_object)
        public_label_object_list = list(public_label_object_set)
        if public_label_object_list == []:
            return [self.get_public_label_object_by_name(self.DEFAULT_PUBLIC_LABEL_NAME)]
        else:
            result = sorted(public_label_object_list, key=lambda x: x.priority)
            return result

    def filter_labels_set_to_public_label_string_list(self, private_labels_set):
        """
        parse the private label to public label name
        :param private_labels_set: string list
        :return:string list
        """
        result_object_list = self.filter_labels_set_to_public_label_object_list(private_labels_set)
        return [label.name for label in result_object_list]

    def get_all_public_label_json_list(self):
        """
        get all public label json data
        :return: a dict list
        """
        labels_json = []
        for label_object in self.public_labels_object_list:
            labels_json.append({"name": label_object.name, "description": label_object.description})
        return labels_json

    def get_all_public_label_name_list(self):
        """
        get all public label json data
        :return: a dict list
        """
        labels_json = []
        for label_object in self.public_labels_object_list:
            labels_json.append(label_object.name)
        return labels_json

    def is_private_property(self, property_name):
        """
        is a property a private
        :param property_name: property key name
        :return:
        """
        if property_name in self.private_property_names:
            return True
        else:
            return False