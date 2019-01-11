import json
import traceback

from gensim import matutils
from numpy.core.multiarray import dot

from db.engine_factory import EngineFactory
from db.model import DomainEntity, APIEntity, APIAlias
from db.search import GeneralConceptEntitySearcher
from model_util.entity_vector.entity_vector_model import EntityVectorModel
from skgraph.graph.accessor.graph_accessor import GraphClient, DefaultGraphAccessor
from skgraph.graph.accessor.graph_client_for_domain_entity import DomainEntityAccessor


class CrossDataSourceFusion:
    useless_alias_type_list = [
        APIAlias.ALIAS_TYPE_SIMPLE_NAME_WITH_TYPE,
        APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
        APIAlias.ALIAS_TYPE_SIMPLE_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE,
        APIAlias.ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
        APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE
    ]

    def __init__(self, max_linkable_concept=5, min_score=0.8):
        self.session = None
        self.wikipedia_vector_map = None
        self.domain_entity_vector_map = None
        self.general_concept_searcher = None
        self.api_entity_vector_map = None
        self.max_linkable_concept = max_linkable_concept
        self.min_score = min_score

    def init(self):
        self.session = EngineFactory.create_session()
        self.wikipedia_vector_map = EntityVectorModel.load("wikipedia.binary.txt", binary=True)
        self.domain_entity_vector_map = EntityVectorModel.load("domain_entity.binary.txt", binary=True)
        self.api_entity_vector_map = EntityVectorModel.load("api.binary.txt", binary=True)

        self.general_concept_searcher = GeneralConceptEntitySearcher(session=self.session)
        print("init complete")

    def read_domain_entity_data(self):
        return DomainEntity.get_all_domain_entity_id_and_name(self.session)

    def read_all_api_entity_data(self):
        return APIEntity.get_all_API_entity(self.session)

    def get_candidate_wiki_set(self, domain_entity_name):
        if domain_entity_name is None:
            return []
        return self.general_concept_searcher.search(domain_entity_name)

    def calculate_similarity_between_domain_and_wiki(self, domain_entity_vector, candidate_wiki_vector):
        if candidate_wiki_vector is not None and domain_entity_vector is not None:
            return dot(matutils.unitvec(candidate_wiki_vector), matutils.unitvec(domain_entity_vector))
        return None

    def get_sorted_candidates(self, domain_entity_vector, candidate_wiki_set):

        if candidate_wiki_set is not None:
            result = {}
            for candidate in candidate_wiki_set:
                try:
                    candidate_kg_id = candidate.kg_id

                    candidate_wiki_vector = self.wikipedia_vector_map["kg#" + str(candidate_kg_id)]
                    similarity = self.calculate_similarity_between_domain_and_wiki(domain_entity_vector,
                                                                                   candidate_wiki_vector)
                    if similarity is not None:
                        result.setdefault(candidate_kg_id, similarity)
                except:
                    traceback.print_exc()

            return sorted(result.items(), key=lambda item: item[1], reverse=True)
        return None

    def get_probable_results(self, sorted_candidate_list, domain_entity_id):
        result = []
        if sorted_candidate_list is not None and domain_entity_id is not None:
            for i in range(0, min(len(sorted_candidate_list), self.max_linkable_concept)):
                if sorted_candidate_list[i][1] > self.min_score:
                    item = (domain_entity_id, sorted_candidate_list[i][0])
                    result.append(item)
        return result

    def get_fusion_result_for_one_domain_entity(self, domain_entity_id, domain_entity_name):
        domain_entity_id = str(domain_entity_id)
        domain_entity_vector = self.domain_entity_vector_map[domain_entity_id]
        candidate_wiki_set = self.get_candidate_wiki_set(domain_entity_name)
        # print("candidate")
        # print(candidate_wiki_set)
        sorted_candidate_list = self.get_sorted_candidates(domain_entity_vector, candidate_wiki_set)
        if sorted_candidate_list is None:
            return []

        propable_result = self.get_probable_results(sorted_candidate_list, domain_entity_id)
        return propable_result

    def start_fusion_for_domain_entity(self, output_file):
        result = []
        count = 0
        domain_entity_data = self.read_domain_entity_data()
        for domain_entity in domain_entity_data:
            # todo,mulprocessor
            # todo:matrix speed up
            try:
                propable_result = self.get_fusion_result_for_one_domain_entity(domain_entity_id=domain_entity.id,
                                                                               domain_entity_name=domain_entity.name)
                result.extend(propable_result)
            except:
                count = count + 1
                traceback.print_exc()
        link_relation_list = []
        for each in result:
            temp = {"domain_entity_id": each[0], "wikipedia_entity_id": each[1]}
            link_relation_list.append(temp)
        with open(output_file, 'w') as f:
            json.dump(link_relation_list, f)
        print("domain_entity num=%d", len(domain_entity_data))
        print("complete relation num=%d", len(link_relation_list))
        print("average relation num=%f", 1.0 * len(link_relation_list) / len(domain_entity_data))
        print("complete error num=%d", count)

    def start_fusion_for_api(self, output_file="api_link_wikidata.json"):
        result = []
        count = 0
        api_entity_datas = self.read_all_api_entity_data()
        for api_entity in api_entity_datas:
            # todo,mulprocessor
            # todo:matrix speed up
            try:
                propable_result = self.get_fusion_result_for_one_api_entity(api_entity=api_entity)
                # print(propable_result)
                result.extend(propable_result)
            except:
                count = count + 1
                traceback.print_exc()
        link_relation_list = []
        for each in result:
            temp = {"api_entity_id": each[0], "wikipedia_entity_id": each[1]}
            link_relation_list.append(temp)
        with open(output_file, 'w') as f:
            json.dump(link_relation_list, f)
        print("domain_entity num=%d", len(api_entity_datas))
        print("complete relation num=%d", len(link_relation_list))
        print("average relation num=%f", 1.0 * len(link_relation_list) / len(api_entity_datas))
        print("complete error num=%d", count)

    def get_fusion_result_for_one_api_entity(self, api_entity):
        api_entity_id = str(api_entity.id)
        api_entity_vector = self.api_entity_vector_map[api_entity_id]

        candidate_wiki_set = self.get_candidate_wiki_set_for_api_entity(api_entity)
        print("candidate")
        # print(candidate_wiki_set)
        sorted_candidate_list = self.get_sorted_candidates(api_entity_vector, candidate_wiki_set)
        if sorted_candidate_list is None:
            return []

        propable_result = self.get_probable_results(sorted_candidate_list, api_entity_id)
        return propable_result

    def get_candidate_wiki_set_for_api_entity(self, api_entity):
        all_aliases = api_entity.all_aliases
        useful_alias_list = set([])
        for alias_entity in all_aliases:
            if alias_entity.type in self.useless_alias_type_list:
                continue
            if api_entity.api_type == APIEntity.API_TYPE_METHOD or api_entity.api_type == APIEntity.API_TYPE_CONSTRUCTOR:
                if alias_entity.type == APIAlias.ALIAS_TYPE_QUALIFIER_NAME:
                    method_alias_need_to_add = alias_entity.alias.split("(")[0]
                    useful_alias_list.add(method_alias_need_to_add)
                    continue
            useful_alias_list.add(alias_entity.alias)

        general_concept_list = []
        for name in useful_alias_list:
            temp_result = self.general_concept_searcher.search(name)
            for temp in temp_result:
                exist = False
                for exist_concept in general_concept_list:
                    if exist_concept.id == temp.id:
                        exist = True
                        break
                if exist == False:
                    general_concept_list.append(temp)

        return general_concept_list


class CrossDataSourceFusionResultKGImporter:
    def __init__(self):
        pass

    def start_import_for_domain_entity(self, linking_result_file):
        graph_client = GraphClient(server_number=4)
        default_graph_client = DefaultGraphAccessor(graph_client)
        domain_entity_graph_client = DomainEntityAccessor(graph_client)
        domain_entity_graph_client.delete_all_domain_entity_to_wikipedia_relation()
        print("delete all old may link relation complete")

        with open(linking_result_file, 'r') as f:
            link_relation_list = json.load(f)

        for each in link_relation_list:
            domain_entity_id = each['domain_entity_id']
            wikipedia_entity_id = each['wikipedia_entity_id']
            if domain_entity_id is None or wikipedia_entity_id is None:
                continue
            domain_entity = domain_entity_graph_client.find_domain_entity_node_by_id(domain_entity_id)
            if domain_entity is None:
                continue
            wikipedia_entity = default_graph_client.find_node_by_id(wikipedia_entity_id)
            if wikipedia_entity is None:
                continue
            domain_entity_graph_client.create_entity_to_general_concept_relation(domain_entity, wikipedia_entity)

    def start_import_for_api_entity(self, linking_result_file):
        graph_client = GraphClient(server_number=4)
        default_graph_client = DefaultGraphAccessor(graph_client)
        api_entity_graph_client = DomainEntityAccessor(graph_client)
        api_entity_graph_client.delete_all_api_entity_to_wikipedia_relation()
        print("delete all old may link relation complete")

        with open(linking_result_file, 'r') as f:
            link_relation_list = json.load(f)

        for each in link_relation_list:
            api_entity_id = each['api_entity_id']
            wikipedia_entity_id = each['wikipedia_entity_id']
            if api_entity_id is None or wikipedia_entity_id is None:
                continue
            api_entity = api_entity_graph_client.find_api_entity_node_by_id(api_entity_id)
            if api_entity is None:
                continue
            wikipedia_entity = default_graph_client.find_node_by_id(wikipedia_entity_id)
            if wikipedia_entity is None:
                continue
            api_entity_graph_client.create_entity_to_general_concept_relation(api_entity, wikipedia_entity)
