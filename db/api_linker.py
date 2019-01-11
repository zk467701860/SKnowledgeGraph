from abc import ABCMeta, abstractmethod

from sqlalchemy import func
from textdistance import LCSStr, Levenshtein, Cosine

from alias_util import Generator, AliasUtil
from engine_factory import EngineFactory
from model import APIEntity, APIAlias


class CandidateSet:
    DEFAULT_FILTER_PROBABILITY = 0.05

    def __init__(self):
        self.candidate_api_set = set()

    def add_api_entity(self, api_entity):
        if isinstance(api_entity, APIEntity):
            self.candidate_api_set.add(CandidateAPI(api_entity))

    def add_api_candidate(self, api_candidate):
        if isinstance(api_candidate, CandidateAPI):
            self.candidate_api_set.add(api_candidate)

    def get_candidate_api_set(self):
        return self.candidate_api_set

    def calculate_probability(self):
        if self.size() <= 1:
            for candidate in self.candidate_api_set:
                candidate.probability = 1.0
                return
        total_score = float(0)
        for candidate in self.candidate_api_set:
            total_score = total_score + candidate.score
        if total_score <= 0:
            for candidate in self.candidate_api_set:
                candidate.probability = 1.0 / self.size()
            return

        for candidate in self.candidate_api_set:
            candidate.probability = candidate.score / total_score

    def sorted_candidate_list(self):
        self.calculate_probability()
        candidate_list = list(self.candidate_api_set)
        candidate_list.sort(key=lambda x: x.probability, reverse=True)

        return candidate_list

    def get_sorted_candidate_dict_list(self, filter_probability=DEFAULT_FILTER_PROBABILITY):
        result = []
        for candidate in self.sorted_candidate_list():
            if candidate.probability > filter_probability:
                result.append(candidate.parse_to_dict())
        return result

    def size(self):
        return len(self.candidate_api_set)

    def possible_candidate_size(self):
        count = 0
        for candidate in self.candidate_api_set:
            if candidate.score > 0:
                count = count + 1
        return count

    def get_valid_candidate_set(self, filter_probability=DEFAULT_FILTER_PROBABILITY):
        valid_candidate_set = CandidateSet()

        for candidate in self.sorted_candidate_list():
            if candidate.probability > filter_probability:
                valid_candidate_set.add_api_candidate(candidate)
        valid_candidate_set.calculate_probability()
        return valid_candidate_set


class CandidateAPI:
    def __init__(self, api_entity, score=0):
        self.api_entity = api_entity
        self.score = score
        self.probability = 0.00
        self.matching_alias = []

    def __eq__(self, other):
        if isinstance(other, CandidateAPI):
            return self.api_entity.id == other.api_entity.id
        else:
            return False

    def __hash__(self):
        return hash(self.api_entity.id)

    def __repr__(self):
        return "CandidateAPI(%s, score=%f, p=%f)" % (self.api_entity, self.score, self.probability)

    def parse_to_dict(self):
        return {
            "api_id": self.api_entity.id,
            "api_qualifier_name": self.api_entity.qualified_name,
            "probability": self.probability
        }

    def add_score(self, score):
        self.score = self.score + score


class APIContext:
    def __init__(self, api_type):
        self.api_type = api_type


class APILinker:
    def __init__(self, session=None):
        if session is None:
            session = EngineFactory.create_session()
        self.session = session
        self.candidate_generator = APICandidateGenerator(session)
        self.scorer_list = []
        self.scorer_list.append(APITypeScorer(weight=35, api_linker=None))
        self.scorer_list.append(MethodParametersScorer(weight=50, api_linker=None))
        self.scorer_list.append(ParentAPIScorer(weight=100.0, api_linker=self))
        self.scorer_list.append(DeclarationScorer(weight=60.0, api_linker=self))

    def link(self, api_name, context, filter_probability=0.05):
        api_candidates_set = self.candidate_generator.generate_candidates(api_name, context)
        if api_candidates_set.size() <= 1:
            return api_candidates_set.get_sorted_candidate_dict_list(filter_probability=filter_probability)

        for scorer in self.scorer_list:
            scorer.score_for_candidate_set(api_candidates_set, api_name, context)

        valid_candidate_set = api_candidates_set.get_valid_candidate_set()
        return valid_candidate_set.get_sorted_candidate_dict_list(filter_probability=filter_probability)


class APICandidateGenerator:
    def __init__(self, session=None):
        if session is None:
            session = EngineFactory.create_session()
        self.session = session

    def generate_candidates(self, api_name, context):
        candidate_set = CandidateSet()

        self.add_candidate_by_alias_exactly_match(api_name,
                                                  candidate_set)
        # the extractly match api by alias is impossible, more way need to be done
        if candidate_set.size() == 0:
            simple_name = AliasUtil.get_simple_name_from_qualifier_name(api_name)
            self.add_candidate_by_alias_exactly_match(simple_name, candidate_set)

        return candidate_set

    def add_candidate_by_alias_exactly_match(self, api_name, candidate_set):
        all_aliases = self.session.query(APIAlias).filter(APIAlias.alias == func.binary(api_name)).all()
        for alias in all_aliases:
            for api in alias.all_apis:
                candidate_set.add_api_entity(api)

    def find_all_apis_match_name(self, api_name):
        pass


class Scorer:
    __metaclass__ = ABCMeta

    def __init__(self, session=None, weight=1.0, api_linker=None):
        self.weight = weight
        self.session = session
        self.api_linker = api_linker

    @abstractmethod
    def is_usable(self, start_api_name, context):
        """
        judge if the scorer is useful for current state
        :param start_api_name: the query api name
        :param context: the link context
        :return:
        """
        return True

    @abstractmethod
    def prepare_global_info(self, start_api_name, context):
        """
        prepare some global info for each score_for_candidate_set to query,not waste time to re calculate
        :param start_api_name: the query api name
        :param context: the link context
        :return:
        """
        return None

    def score_for_candidate_set(self, api_candidates_set, api_name, context):
        """
        the default score all candidates in the candidate set,
         can be override to support some time consuming operation in this method global
        :param api_candidates_set: the APICandidateSet
        :param api_name: the start api name
        :param context: the api context
        :return:
        """
        if not self.is_usable(api_name,context):
            return

        global_info = self.prepare_global_info(api_name,context)

        for candidate_api in api_candidates_set.get_candidate_api_set():
            new_score = self.score_with_weight(api_name, candidate_api.api_entity, context, global_info)
            candidate_api.add_score(new_score)

    @abstractmethod
    def score_api_entity_without_weight(self, start_api_name, api_entity, context, global_info=None):
        """
        score the api entity
        :param global_info: the global info for score one candidate set,
         in case some waste time query when score evry api_entity_alias
        :param start_api_name: the start query api name
        :param api_entity: the candidate api entity
        :param context: the context for scorer
        :return: a score
        """
        return 0.0

    def score_with_weight(self, start_api_name, api_entity, context, global_info=None):
        """
        score the api entity
        :param global_info:
        :param start_api_name: the start query api name
        :param api_entity: the candidate api entity
        :param context: the context for scorer
        :return: a score
        """
        return self.score_api_entity_without_weight(start_api_name, api_entity, context, global_info) * self.weight


class APITypeScorer(Scorer):
    """
    Score the api entity with the start api name
    """

    def prepare_global_info(self, start_api_name, context):
        return None

    def is_usable(self, start_api_name, context):
        actual_api_type_string = None
        if not context:
            return False
        if "api_type" in context:
            actual_api_type_string = context["api_type"]

        # not valid api type
        if not actual_api_type_string or actual_api_type_string == "null":
            return False

        return True

    lcsstr = LCSStr()
    levenshtein = Levenshtein()
    cosine = Cosine()

    def score_api_entity_without_weight(self, start_api_name, api_entity, context, global_info=None):
        """
        score the api entity
        :param global_info: the global info for score one candidate set,
         in case some waste time query when score evry api_entity_alias
        :param start_api_name: the start query api name
        :param api_entity: the candidate api entity
        :param context: the context for scorer
        :return: a score
        """

        actual_api_type_string = context["api_type"]

        if api_entity.api_type == APIEntity.API_TYPE_UNKNOWN:
            return 0

        actual_api_type = APIEntity.type_string_to_api_type_constant(actual_api_type_string)
        if actual_api_type == APIEntity.API_TYPE_UNKNOWN:
            candidate_api_entity_string_list = APIEntity.get_api_type_string(api_entity.api_type)
            return self.get_string_similarity(actual_api_type_string, candidate_api_entity_string_list)
        else:
            return self.calculate_api_type_similarity(actual_api_type, api_entity.api_type)

    def get_string_similarity(self, actual_api_type_string, candidate_api_entity_string_list):
        scores = []
        if len(candidate_api_entity_string_list) == 0:
            return 0
        for candidate_api_entity_string in candidate_api_entity_string_list:
            similarity = self.calculate_the_type_string_similarity(actual_api_type_string, candidate_api_entity_string)
            scores.append(similarity)
        return max(scores)

    def calculate_the_type_string_similarity(self, actual_type_string, candidate_string):
        lcsstr_similarity = self.lcsstr.normalized_similarity(actual_type_string.lower(), candidate_string.lower())
        levenshtein_similarity = self.levenshtein.normalized_similarity(actual_type_string.lower(),
                                                                        candidate_string.lower())
        cosine_similarity = self.cosine.normalized_similarity(actual_type_string.lower(),
                                                              candidate_string.lower())

        return 0.3 * lcsstr_similarity + 0.3 * levenshtein_similarity + 0.4 * cosine_similarity

    @staticmethod
    def calculate_api_type_similarity(actual_type, candidate_type):
        if actual_type == candidate_type:
            return 1.0
        if APIEntity.api_type_belong_to_relation(candidate_type, actual_type):
            return 0.9
        if APIEntity.api_type_belong_to_relation(actual_type, candidate_type):
            return 0.1
        # todo some type contain relation need to defined
        return 0.0


class DeclarationScorer(Scorer):
    """
    Score the api entity with the start api name
    """

    def is_usable(self, start_api_name, context):
        declaration = None
        if not context:
            return False
        if "declaration" in context:
            declaration = context["declaration"]

        # not valid api type
        if not declaration or declaration == "null":
            return False

        main_declaration_string = AliasUtil.get_main_declaration_string(declaration)
        if not main_declaration_string:
            return False

        return True

    def prepare_global_info(self, start_api_name, context):
        declaration = context["declaration"]
        main_declaration_string = AliasUtil.get_main_declaration_string(declaration)

        return {"main_declaration_string": main_declaration_string}

    lcsstr = LCSStr()
    levenshtein = Levenshtein()
    cosine = Cosine()

    def score_api_entity_without_weight(self, start_api_name, api_entity, context, global_info=None):
        """
        score the api entity
        :param global_info: the global info for score one candidate set,
        in case some waste time query when score evry api_entity_alias
        :param start_api_name: the start query api name
        :param api_entity: the candidate api entity
        :param context: the context for scorer
        :return: a score
        """
        main_declaration_string = global_info["main_declaration_string"]

        return self.calculate_the_type_string_similarity(main_declaration_string, api_entity.qualified_name)

    def calculate_the_type_string_similarity(self, actual_type_string, candidate_string):
        lcsstr_similarity = self.lcsstr.normalized_similarity(actual_type_string.lower(), candidate_string.lower())
        levenshtein_similarity = self.levenshtein.normalized_similarity(actual_type_string.lower(),
                                                                        candidate_string.lower())
        cosine_similarity = self.cosine.normalized_similarity(actual_type_string.lower(),
                                                              candidate_string.lower())

        return 0.3 * lcsstr_similarity + 0.3 * levenshtein_similarity + 0.4 * cosine_similarity


class MethodParametersScorer(Scorer):
    """
    Score the api entity with the parameters match, only for the method parameters
    """

    def is_usable(self, start_api_name, context):
        return True

    def prepare_global_info(self, start_api_name, context):
        return None

    @staticmethod
    def is_method(name):
        if "(" in name and ")" in name:
            return True
        return False

    @staticmethod
    def get_parameters_num(name):
        name = name.replace("<.*?>", "")
        seperate_words = name.split("(", 1)
        parameters_string = seperate_words[1].split(")", 1)[0]

        if parameters_string.strip() == "":
            return 0

        return len(parameters_string.split(","))

    def score_api_entity_without_weight(self, start_api_name, api_entity, context, global_info=None):
        """
        score the api entity
        :param global_info: the global info for score one candidate set,
         in case some waste time query when score evry api_entity_alias
        :param start_api_name: the start query api name
        :param api_entity: the candidate api entity
        :param context: the context for scorer
        :return: a score
        """

        similarity_list = []

        similarity = self.get_parameter_similarity(api_entity, start_api_name)
        similarity_list.append(similarity)

        declaration_similarity = self.get_parameter_similarity_from_declaration(api_entity, context)
        similarity_list.append(declaration_similarity)

        return max(similarity_list)

    def get_parameter_similarity_from_declaration(self, api_entity, context):
        if not context:
            return 0
        declaration = None
        if "declaration" in context:
            declaration = context["declaration"]

        # not valid api type
        if not declaration or declaration == "null":
            return 0

        main_declaration = AliasUtil.get_main_declaration_string(declaration)
        declaration_similarity = self.get_parameter_similarity(api_entity, main_declaration)
        return declaration_similarity

    def get_parameter_similarity(self, api_entity, start_api_name):
        if not start_api_name:
            return 0.0
        if not MethodParametersScorer.is_method(start_api_name):
            return 0.0

        # the candidate must be method, so it can be match
        if api_entity.api_type != APIEntity.API_TYPE_METHOD and api_entity.api_type != APIEntity.API_TYPE_CONSTRUCTOR:
            return 0.0
        old_parameters_num = self.get_parameters_num(start_api_name)
        candidate_parameters_num = self.get_parameters_num(api_entity.qualified_name)
        # todo :add match for parameters type,not only the parameter's type
        if old_parameters_num == candidate_parameters_num:
            return 1.0
        else:
            return 0.0


class ParentAPIScorer(Scorer):
    def prepare_global_info(self, start_api_name, context):
        parent_api = self.get_parent_api(context)
        parent_api_link_results = self.api_linker.link(parent_api, None)
        return {"parent_api_link_results": parent_api_link_results}

    def is_usable(self, start_api_name, context):
        if not context:
            return False
        parent_api = self.get_parent_api(context)
        if not parent_api:
            return False

        return True

    def score_api_entity_without_weight(self, start_api_name, api_entity, context, global_info=None):
        """
        score the api entity
        :param global_info: the global info for score one candidate set,
        in case some waste time query when score evry api_entity_alias
        :param start_api_name: the start query api name
        :param api_entity: the candidate api entity
        :param context: the context for scorer
        :return: a score
        """

        parent_api = context["parent_api"]
        return self.get_score_for_by_parent_api_without_weight(api_entity, parent_api,
                                                               global_info["parent_api_link_results"])

    @staticmethod
    def get_parent_api(context):
        parent_api = None
        if "parent_api" in context:
            parent_api = context["parent_api"]
        return parent_api

    def get_score_for_by_parent_api_without_weight(self, api_entity, parent_api, parent_api_link_results=None):
        count = 0
        if not parent_api_link_results:
            parent_api_link_results = self.api_linker.link(parent_api, None)
        for candidate_parent_api_link in parent_api_link_results:
            if candidate_parent_api_link <= 0.2:
                # no use link
                continue

            parent_api_qualifier_name = candidate_parent_api_link["api_qualifier_name"]
            # todo: fix the api_qualifier_name not match with api_qualified_name problem

            qualified_name = api_entity.qualified_name.split("(")[0]
            if parent_api_qualifier_name + "." in qualified_name:
                count = count + 1
        if count == 0:
            score = 0
        else:
            score = 1.0 / count

        return score
