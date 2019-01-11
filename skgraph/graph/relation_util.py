class RelationUtil:
    def __init__(self, graph_accessor):
        self.graph_accessor = graph_accessor
        self.relation_description_map = {}
        self.init_relation_description()

    def init_relation_description(self):
        if self.graph_accessor == None:
            return

        relation_nodes = self.graph_accessor.get_all_relation_nodes()

        relation_description_map = {}
        for r in relation_nodes:

            description = r["descriptions_en"]
            if description is None:
                continue

            name = r["name"]
            if name is None:
                name = r["labels_en"]
            if name is None:
                continue
            relation_description_map[name] = description
            aliases_list = r["aliases_en"]
            if aliases_list is None:
                continue
            for alias in aliases_list:
                relation_description_map[alias] = description

        self.relation_description_map = relation_description_map

    def get_description_by_relation_type(self, relation_type):
        if relation_type in self.relation_description_map.keys():
            return self.relation_description_map[relation_type]
        else:
            return relation_type

    def get_relation_description_json(self, relation_type):
        return {"name": relation_type, "description": self.get_description_by_relation_type(relation_type)}

    def get_relation_description_json_list(self, relation_type_list):
        result_list = []
        for type in relation_type_list:
            result_list.append(self.get_relation_description_json(type))
        return result_list
