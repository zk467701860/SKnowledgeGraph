import re
import traceback
from abc import ABCMeta, abstractmethod

from engine_factory import EngineFactory
from model import APIAlias, APIEntity
from shared.logger_util import Logger


class DerivedAliasGenerator(object):
    __metaclass__ = ABCMeta

    # todo: complete this for genericity and "..."
    def __init__(self):
        pass

    @abstractmethod
    def generate_aliases(self, api_entity):
        pass


class Generator(object):
    __metaclass__ = ABCMeta

    def __init__(self, alias_type):
        self.alias_type = alias_type

    @abstractmethod
    def generate_aliases(self, api_entity):
        pass

    @staticmethod
    def get_simple_name_from_qualifier_name(qualifier_name):
        if qualifier_name == "...":
            return "..."
        team_name = qualifier_name.split("(")[0]
        return team_name.split(".")[-1]


class QualifierNameGenerator(Generator):
    def generate_aliases(self, api_entity):
        alias_name = api_entity.qualified_name
        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class SimpleNameGenerator(Generator):
    def generate_aliases(self, api_entity):
        alias_name = AliasUtil.get_simple_name_from_qualifier_name(api_entity.qualified_name)
        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class TypedSimpleNameGenerator(Generator):
    @staticmethod
    def get_simple_name_with_type_list(qualifier_name, api_type):
        simple_name = AliasUtil.get_simple_name_from_qualifier_name(qualifier_name)
        api_type_strings = APIEntity.get_api_type_string(api_type)
        alias_names = []
        if api_type_strings:
            for api_type_string in api_type_strings:
                alias_names.append(api_type_string + " " + simple_name)
        return alias_names

    def generate_aliases(self, api_entity):
        result = []
        alias_name_list = TypedSimpleNameGenerator.get_simple_name_with_type_list(api_entity.qualified_name,
                                                                                  api_entity.api_type)
        for alias_name in alias_name_list:
            api_alias = APIAlias(alias_name, self.alias_type)
            result.append(api_alias)

        return result


class SimpleMethodWithQualifierParameterTypeGenerator(Generator):
    @staticmethod
    def get_method_qualifier_parameter_type(qualifier_name):
        simple_name = AliasUtil.get_simple_name_from_qualifier_name(qualifier_name)
        parameters = qualifier_name.split("(")[1]
        return simple_name + "(" + parameters

    def generate_aliases(self, api_entity):
        alias_name = SimpleMethodWithQualifierParameterTypeGenerator.get_method_qualifier_parameter_type(
            api_entity.qualified_name)
        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class SimpleClassNameMethodWithQualifierParameterTypeGenerator(Generator):
    @staticmethod
    def get_alias_name(qualifier_name):
        team_name = qualifier_name.split("(")[0]
        words = team_name.split(".")
        if len(words) >= 3:
            alias_name = words[-2] + "." + words[-1] + "(" + qualifier_name.split("(")[1]
            return alias_name
        else:
            return None

    def generate_aliases(self, api_entity):
        qualifier_name = api_entity.qualified_name
        if "(" not in qualifier_name:
            return []
        alias_name = self.get_alias_name(qualifier_name)
        if not alias_name:
            return []

        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class SimpleMethodWithSimpleParameterTypeGenerator(Generator):
    @staticmethod
    def replace_qualifier_name_with_simple_name(string):
        result_string = ""
        current_string = ""
        for char in string:
            if char == "(" or char == ")" or char == "<" or char == ">" or char == " " or char == ",":
                current_string = AliasUtil.get_simple_name_from_qualifier_name(current_string)
                result_string = result_string + current_string
                current_string = ""
                result_string = result_string + char
            else:
                current_string = current_string + char

        result_string = result_string + AliasUtil.get_simple_name_from_qualifier_name(current_string)

        return result_string

    @staticmethod
    def get_alias_name(qualifier_name):
        team_name = qualifier_name.split("(")[0]
        words = team_name.split(".")
        method_name = words[-1]

        parameters_list_string = qualifier_name.split("(")[-1].strip(")")

        if parameters_list_string == "":
            return "{method_name}({parameters})".format(method_name=method_name,
                                                        parameters="")

        parameters_string = SimpleMethodWithSimpleParameterTypeGenerator.replace_qualifier_name_with_simple_name(
            parameters_list_string)

        return "{method_name}({parameters})".format(method_name=method_name,
                                                    parameters=parameters_string)

    def generate_aliases(self, api_entity):
        qualifier_name = api_entity.qualified_name
        if "(" not in qualifier_name:
            return []
        try:
            alias_name = self.get_alias_name(qualifier_name)
        except Exception:
            traceback.print_exc()
            alias_name = None
        if not alias_name:
            return []

        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class SimpleClassMethodWithSimpleParameterTypeGenerator(Generator):
    @staticmethod
    def replace_qualifier_name_with_simple_name(string):
        result_string = ""
        current_string = ""
        for char in string:
            if char == "(" or char == ")" or char == "<" or char == ">" or char == " " or char == ",":
                current_string = AliasUtil.get_simple_name_from_qualifier_name(current_string)
                result_string = result_string + current_string
                current_string = ""
                result_string = result_string + char
            else:
                current_string = current_string + char

        result_string = result_string + AliasUtil.get_simple_name_from_qualifier_name(current_string)

        return result_string

    @staticmethod
    def get_alias_name(qualifier_name):
        team_name = qualifier_name.split("(")[0]
        words = team_name.split(".")
        if len(words) >= 2:
            method_name = words[-2] + "." + words[-1]
        else:
            return None
        parameters_list_string = qualifier_name.split("(")[-1].strip(")")

        if parameters_list_string == "":
            return "{method_name}({parameters})".format(method_name=method_name,
                                                        parameters="")

        parameters_string = SimpleClassMethodWithSimpleParameterTypeGenerator.replace_qualifier_name_with_simple_name(
            parameters_list_string)

        return "{method_name}({parameters})".format(method_name=method_name,
                                                    parameters=parameters_string)

    def generate_aliases(self, api_entity):
        qualifier_name = api_entity.qualified_name
        if "(" not in qualifier_name:
            return []
        alias_name = self.get_alias_name(qualifier_name)
        if not alias_name:
            return []

        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class SimpleParentAPINameWithSimpleName(Generator):
    def get_alias_name(self, qualifier_name):
        words = qualifier_name.split(".")
        if len(words) >= 2:
            return words[-2] + "." + words[-1]
        return None

    def generate_aliases(self, api_entity):
        qualified_name = api_entity.qualified_name

        alias_name = self.get_alias_name(qualified_name)
        if not alias_name:
            return []

        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class AnnotationAliasGenerator(Generator):
    def get_alias_name(self, qualifier_name):
        words = qualifier_name.split(".")
        if len(words) > 1:
            return "@" + words[-1]
        return None

    def generate_aliases(self, api_entity):
        qualified_name = api_entity.qualified_name

        alias_name = self.get_alias_name(qualified_name)
        if not alias_name:
            return []

        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class CamelCaseGenerator(Generator):
    def get_alias_name(self, qualifier_name):
        simple_name = AliasUtil.get_simple_name_from_qualifier_name(qualifier_name)
        alias_name = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', simple_name)
        if alias_name == simple_name:
            return None
        return alias_name

    def generate_aliases(self, api_entity):
        qualified_name = api_entity.qualified_name

        alias_name = self.get_alias_name(qualified_name)
        if not alias_name:
            return []

        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class ValueAliasGenerator(Generator):

    def generate_aliases(self, api_entity):
        qualified_name = api_entity.qualified_name
        declaration = api_entity.full_declaration

        return [APIAlias(qualified_name, self.alias_type), APIAlias(declaration, self.alias_type)]


class UnderlineGenerator(Generator):
    def get_alias_name(self, qualifier_name):
        simple_name = AliasUtil.get_simple_name_from_qualifier_name(qualifier_name)

        alias_name = simple_name.replace('_', ' ')

        if simple_name == alias_name:
            return None
        return alias_name

    def generate_aliases(self, api_entity):
        qualified_name = api_entity.qualified_name

        alias_name = self.get_alias_name(qualified_name)
        if not alias_name:
            return []

        api_alias = APIAlias(alias_name, self.alias_type)
        return [api_alias]


class APIAliasGeneratorFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_generator(alias_type):
        if alias_type == APIAlias.ALIAS_TYPE_SIMPLE_NAME:
            return SimpleNameGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_QUALIFIER_NAME:
            return QualifierNameGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_SIMPLE_NAME_WITH_TYPE:
            return TypedSimpleNameGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE:
            return SimpleMethodWithQualifierParameterTypeGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE:
            return SimpleClassNameMethodWithQualifierParameterTypeGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_SIMPLE_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE:
            return SimpleMethodWithSimpleParameterTypeGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE:
            return SimpleClassMethodWithSimpleParameterTypeGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_SIMPLE_PARENT_API_NAME_WITH_SIMPLE_NAME:
            return SimpleParentAPINameWithSimpleName(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_ANNOTATION_REFERENCE:
            return AnnotationAliasGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_CAMEL_CASE_TO_SPACE:
            return CamelCaseGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_UNDERLINE_TO_SPACE:
            return UnderlineGenerator(alias_type)
        if alias_type == APIAlias.ALIAS_TYPE_VALUE_ALIAS:
            return ValueAliasGenerator(alias_type)

        return None


class APIAliasesTableFuller:
    ALL_API = -1

    def __init__(self, table=APIEntity.__tablename__, session=None, commit_step=5000):
        self.table = table
        self.commit_step = commit_step
        self.logger_file_name = "generate_api_aliases"
        self.logger = None
        self.session = session
        self.api_html_table = None
        self.api_knowledge_table = None
        self.data_source_knowledge_table = None

    def get_session(self):
        if not self.session:
            self.session = EngineFactory.create_session()

        return self.session

    def start_fix_exist_aliases_for_aliases_type(self, alias_type):
        pass

        self.logger = Logger(self.logger_file_name).get_log()
        self.logger.info("-----------------------start-----------------------")
        self.logger.info("generate api aliases for alias type=%d", alias_type)

        session = self.get_session()

    def start_generate_aliases_for_api_type(self, alias_type, api_type=ALL_API):
        self.logger = Logger(self.logger_file_name).get_log()
        self.logger.info("-----------------------start-----------------------")
        self.logger.info("generate api aliases for api type=%d alias type=%d", api_type, alias_type)

        session = self.get_session()

        api_alias_generator = APIAliasGeneratorFactory.create_generator(alias_type)
        if api_alias_generator is None:
            self.logger.error("Not Implemented Generator for %d ", alias_type)
            return

        if api_type == APIAliasesTableFuller.ALL_API:
            count_api = session.query(APIEntity).count()
            api_list_query = session.query(APIEntity)
        else:
            count_api = session.query(APIEntity).filter(APIEntity.api_type == api_type).count()
            api_list_query = session.query(APIEntity).filter(APIEntity.api_type == api_type)

        start_index_list = range(0, count_api, self.commit_step)

        for start_index in start_index_list:
            end_index = min(start_index + self.commit_step, count_api)
            for api in api_list_query.all()[start_index:end_index]:
                try:
                    api_alias_list = api_alias_generator.generate_aliases(api)
                    self.add_aliases_to_api_entity(api, api_alias_list, session)
                except Exception:
                    traceback.print_exc()

            self.logger.info("complete %d-%d", start_index, end_index)
            session.commit()
        self.logger.info("complete all")

    def start_generate_aliases_for_multi_api_type(self, alias_type, *api_type_list):
        for api_type in api_type_list:
            self.start_generate_aliases_for_api_type(alias_type=alias_type, api_type=api_type)

    def add_aliases_to_api_entity(self, api, api_alias_list, session):
        for api_alias in api_alias_list:
            api_alias = api_alias.find_or_create(session=session, autocommit=False)
            self.logger.info(api)
            self.logger.info(api_alias)

            if api_alias not in api.all_aliases:
                api.all_aliases.append(api_alias)

    def clean_table(self):
        APIAlias.delete_all(session=self.session)
    def start_add_all_api_aliases(self):
        self.clean_table()
        self.start_generate_aliases_for_api_type(APIAlias.ALIAS_TYPE_QUALIFIER_NAME)
        self.start_generate_aliases_for_api_type(APIAlias.ALIAS_TYPE_SIMPLE_NAME)
        # fuller.start_generate_aliases_for_api_type(APIAlias.ALIAS_TYPE_SIMPLE_NAME_WITH_TYPE)
        self.start_generate_aliases_for_multi_api_type(
            APIAlias.ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
            APIEntity.API_TYPE_METHOD, APIEntity.API_TYPE_CONSTRUCTOR)

        self.start_generate_aliases_for_multi_api_type(
            APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
            APIEntity.API_TYPE_CONSTRUCTOR, APIEntity.API_TYPE_METHOD)

        self.start_generate_aliases_for_multi_api_type(
            APIAlias.ALIAS_TYPE_SIMPLE_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE,
            APIEntity.API_TYPE_METHOD, APIEntity.API_TYPE_CONSTRUCTOR)

        self.start_generate_aliases_for_multi_api_type(
            APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE,
            APIEntity.API_TYPE_METHOD, APIEntity.API_TYPE_CONSTRUCTOR)
        self.start_generate_aliases_for_multi_api_type(
            APIAlias.ALIAS_TYPE_SIMPLE_PARENT_API_NAME_WITH_SIMPLE_NAME,
            APIEntity.API_TYPE_ENUM_CONSTANTS, APIEntity.API_TYPE_FIELD, APIEntity.API_TYPE_INTERFACE,
            APIEntity.API_TYPE_EXCEPTION, APIEntity.API_TYPE_PACKAGE, APIEntity.API_TYPE_ANNOTATION,
            APIEntity.API_TYPE_ERROR)

        self.start_generate_aliases_for_api_type(
            APIAlias.ALIAS_TYPE_ANNOTATION_REFERENCE,
            APIEntity.API_TYPE_ANNOTATION)

        self.start_generate_aliases_for_multi_api_type(
            APIAlias.ALIAS_TYPE_CAMEL_CASE_TO_SPACE,
            APIEntity.API_TYPE_CLASS,
            APIEntity.API_TYPE_INTERFACE,
            APIEntity.API_TYPE_EXCEPTION,
            APIEntity.API_TYPE_ERROR,
            APIEntity.API_TYPE_ENUM_CLASS,
            APIEntity.API_TYPE_ANNOTATION,
            APIEntity.API_TYPE_METHOD,
            APIEntity.API_TYPE_CONSTRUCTOR
        )
        print("finished")
        self.start_generate_aliases_for_multi_api_type(
            APIAlias.ALIAS_TYPE_UNDERLINE_TO_SPACE,
            APIEntity.API_TYPE_CLASS,
            APIEntity.API_TYPE_INTERFACE,
            APIEntity.API_TYPE_EXCEPTION,
            APIEntity.API_TYPE_ERROR,
            APIEntity.API_TYPE_ENUM_CLASS,
            APIEntity.API_TYPE_ANNOTATION,
            APIEntity.API_TYPE_FIELD,
            APIEntity.API_TYPE_METHOD,
            APIEntity.API_TYPE_CONSTRUCTOR
        )
        print("finished")

class AliasUtil:
    def __init__(self):
        pass

    @staticmethod
    def get_main_declaration_string(declaration):
        if ")" in declaration and "(" in declaration:
            right_declaration_string = declaration.split(")", 1)[0]

            words = right_declaration_string.split("(", 1)

            method_name = words[0].split(" ")[-1]

            return method_name + "(" + words[1] + ")"
        return None

    @staticmethod
    def get_simple_name_from_qualifier_name(qualifier_name):
        if qualifier_name == "...":
            return "..."
        team_name = qualifier_name.split("(")[0]
        return team_name.split(".")[-1]

