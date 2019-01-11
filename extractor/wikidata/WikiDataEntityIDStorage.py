import codecs
import json
import os


class WikiDataEntityIDStorage:
    '''
    store the accept id and deny id
    '''

    def __init__(self):
        self.accept_id_file_path = os.path.join(".", 'wd_entity_id_map.txt')
        self.deny_id_file_path = os.path.join(".", 'deny_wd_entity_id_map.txt')
        self.accept_entity_id_set = set()
        self.deny_entity_id_set = set()
        self.old_deny_id_num = 0
        self.old_accept_id_num = 0

    def accept_id_set_empty(self):
        return len(self.accept_entity_id_set) == 0

    def deny_id_set_empty(self):
        return len(self.deny_entity_id_set) == 0

    def load(self, id_file_dir_path='.', accept_id_file_name='wd_entity_id_map.txt',
             deny_id_file_name='deny_wd_entity_id_map.txt', ):
        self.accept_id_file_path = os.path.join(id_file_dir_path, accept_id_file_name)
        if os.path.isfile(self.accept_id_file_path):
            self.accept_entity_id_set = set(json.load(codecs.open(self.accept_id_file_path, 'r', 'utf-8')))
        self.deny_id_file_path = os.path.join(id_file_dir_path, deny_id_file_name)
        if os.path.isfile(self.deny_id_file_path):
            self.deny_entity_id_set = set(json.load(codecs.open(self.deny_id_file_path, 'r', 'utf-8')))

        self.old_deny_id_num = len(self.deny_entity_id_set)
        self.old_accept_id_num = len(self.accept_entity_id_set)

    def save(self):
        accept_id_num = len(self.accept_entity_id_set)
        if self.old_accept_id_num != accept_id_num:
            json.dump(list(self.accept_entity_id_set), codecs.open(self.accept_id_file_path, 'w', 'utf-8'))
            self.old_accept_id_num = accept_id_num
        deny_id_num = len(self.deny_entity_id_set)
        if self.old_deny_id_num != deny_id_num:
            json.dump(list(self.deny_entity_id_set), codecs.open(self.deny_id_file_path, 'w', 'utf-8'))
            self.old_deny_id_num = deny_id_num

    def remove(self, *id_list):
        self.accept_entity_id_set = self.accept_entity_id_set - set(id_list)
        self.save()

    def exist(self, id):
        if id in self.accept_entity_id_set:
            return True
        else:
            return False

    def deny_id_exist(self, id):
        if id in self.deny_entity_id_set:
            return True
        else:
            return False

    def add_accept_ids(self, *id_list):
        new_set = set(id_list)
        # remove unexpected id in new id list,get the legal ids
        new_set = new_set - self.deny_entity_id_set

        # get the ids not in  accept_entity_id_set
        new_set = new_set - self.accept_entity_id_set
        self.accept_entity_id_set.update(new_set)
        self.save()
        return new_set

    def add_deny_ids(self, *id_list):
        new_set = set(id_list)
        # remove unexpected id in new id list,get the legal ids
        self.deny_entity_id_set.update(new_set)
        self.accept_entity_id_set = self.accept_entity_id_set - new_set
        self.save()
        return new_set

    def get_accept_id_list(self):
        return list(self.accept_entity_id_set)

    def size(self):
        return len(self.accept_entity_id_set)
