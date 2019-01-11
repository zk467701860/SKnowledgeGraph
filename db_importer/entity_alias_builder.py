# coding=utf-8
from db.engine_factory import EngineFactory
from db.model import EntityForQA, APIEntity, WikipediaEntityName, APIAlias
from db_importer.general_concept import WikiAliasDBImporter
from skgraph.graph.accessor.graph_accessor import GraphClient, DefaultGraphAccessor
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor
from skgraph.graph.accessor.graph_client_for_domain_entity import DomainEntityAccessor


class EntityAliasesBuilder:
    def __init__(self):
        self.session = None

    def init(self):
        self.session = EngineFactory.create_session()

    def clear_table(self):
        EntityForQA.clear_table(self.session)

    def build_aliases(self):
        self.clear_table()
        self.build_aliases_for_api()
        self.build_aliases_for_domain_entity()
        self.build_aliases_for_wikidata()

    def build_aliases_for_api(self):
        # fuller = APIAliasesTableFuller()
        # fuller.start_add_all_api_aliases()
        useless_alias_type_list = [
            APIAlias.ALIAS_TYPE_QUALIFIER_NAME,
            APIAlias.ALIAS_TYPE_SIMPLE_NAME_WITH_TYPE,
            APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
            APIAlias.ALIAS_TYPE_SIMPLE_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE,
            APIAlias.ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
            APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE
        ]

        EntityForQA.delete_names_by_source(session=self.session, source="api")
        accessor = APIGraphAccessor(GraphClient(server_number=4))
        pair_list = accessor.get_all_api_id_and_kg_id_pair()
        for pair in pair_list:
            name_set = set([])
            api_entity = APIEntity.find_by_id(session=self.session, api_entity_id=pair["api_id"])
            all_aliases = api_entity.all_aliases
            for alias_entity in all_aliases:
                if alias_entity.type in useless_alias_type_list:
                    continue
                if api_entity.api_type == APIEntity.API_TYPE_METHOD or api_entity.api_type == APIEntity.API_TYPE_CONSTRUCTOR:
                    if alias_entity.type == APIAlias.ALIAS_TYPE_QUALIFIER_NAME:
                        method_alias_need_to_add = alias_entity.alias.split("(")[0]
                        package_split_list = method_alias_need_to_add.split(".")
                        if len(package_split_list)>=2:
                            alias = package_split_list[-2] + "." + package_split_list[-1]
                            print("add method name=", alias)
                            name_set.add(alias)
                            name_set.add(package_split_list[-1])
                        else:
                            name_set.add(package_split_list[-1])
                        continue
                if api_entity.api_type == APIEntity.API_TYPE_PARAMETER or api_entity.api_type == APIEntity.API_TYPE_RETURN_VALUE:
                    continue
                name_set.add(alias_entity.alias)
            for name in name_set:
                entity = EntityForQA(kg_id=pair["kg_id"], entity_id=pair["api_id"], source="api",
                                     attr='api_id', attr_value=name)
                self.session.add(entity)
        self.session.commit()

    def build_aliases_for_domain_entity(self):

        EntityForQA.delete_names_by_source(session=self.session, source="domain entity")

        client = GraphClient(server_number=4)
        accessor = DomainEntityAccessor(client)
        default_accessor = DefaultGraphAccessor(client)
        domain_entity_list = accessor.get_all_domain_entity()
        for domain_entity in domain_entity_list:
            entity = EntityForQA(kg_id=default_accessor.get_id_for_node(node=domain_entity),
                                 entity_id=domain_entity['domain_entity_id'], source="domain entity",
                                 attr='domain_entity_id', attr_value=domain_entity['domain_entity:name'])

            self.session.add(entity)
        self.session.commit()

    def build_aliases_for_wikidata(self):
        importer = WikiAliasDBImporter()
        importer.start_import()
        wikipedia_name_entity_list = WikipediaEntityName.get_all_wikipedia_names(session=self.session)

        for wikipedia_name in wikipedia_name_entity_list:
            entity = EntityForQA(kg_id=wikipedia_name.kg_id,
                                 entity_id=None, source="wikidata",
                                 attr='wikipedia', attr_value=wikipedia_name.name)

            self.session.add(entity)
        self.session.commit()
