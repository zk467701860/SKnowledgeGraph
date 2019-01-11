import json

from db.engine_factory import EngineFactory
from db.model import DomainEntityExtractFromSentenceRelation, DomainEntity


class APClusterResultDBImporterPipeline:
    def __init__(self):
        self.session = None

    def init(self):
        self.session = EngineFactory.create_session()

    def clean_table(self):
        print("delete all domain entity their relation")
        DomainEntityExtractFromSentenceRelation.delete_all(session=self.session)
        print("delete all domain entity")
        DomainEntity.delete_all(session=self.session)
        print("complete delete")

    def import_ap_cluster_result_for_entity(self, domain_entity_list):
        for domain_entity in domain_entity_list:
            source_id = domain_entity['id']
            name = domain_entity['noun_phrase']
            sub_nodes = domain_entity['sub_nodes']
            description =  domain_entity['sentence']
            for node in sub_nodes:
                description +="\n"+ node['sentence']
            # print "source_id: ", source_id, ", name: ", name, ", description: ", description
            if source_id is not None and name is not None and description is not None:
                document_domain_entity = DomainEntity(name=name, description=description, source_id=source_id)
                document_domain_entity.find_or_create(self.session, autocommit=False)
        self.session.commit()
        print("import entity done")

    def import_ap_cluster_result_for_relation(self, domain_entity_list):
        session = self.session

        for each in domain_entity_list:
            source_id = each['id']
            domain_entity = DomainEntity.get_by_source_id(session, source_id)
            if domain_entity is not None:
                domain_entity_id = domain_entity.id
                sub_nodes = each['sub_nodes']
                if sub_nodes is not None:
                    for node in sub_nodes:
                        sentence_id = node['sentence_id']
                        if sentence_id is not None:
                            relation = DomainEntityExtractFromSentenceRelation(sentence_id, domain_entity_id)
                            relation.find_or_create(session, autocommit=False)
        session.commit()
        print("import relation done")

    def get_domain_entity_list(self, filename):
        with open(filename, 'r') as f:
            domain_entity_list = json.load(f)
        print("load json done")
        return domain_entity_list

    def start_import_entity_and_relation(self, filename):
        self.clean_table()
        domain_entity_list = self.get_domain_entity_list(filename)
        self.import_ap_cluster_result_for_entity(domain_entity_list)
        self.import_ap_cluster_result_for_relation(domain_entity_list)
