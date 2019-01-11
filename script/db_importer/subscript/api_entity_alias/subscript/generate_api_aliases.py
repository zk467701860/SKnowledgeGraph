from db.alias_util import APIAliasesTableFuller
from db.model import APIAlias, APIEntity

if __name__ == "__main__":
    fuller = APIAliasesTableFuller()
    fuller.start_generate_aliases_for_api_type(APIAlias.ALIAS_TYPE_QUALIFIER_NAME)
    fuller.start_generate_aliases_for_api_type(APIAlias.ALIAS_TYPE_SIMPLE_NAME)
    fuller.start_generate_aliases_for_api_type(APIAlias.ALIAS_TYPE_SIMPLE_NAME_WITH_TYPE)
    fuller.start_generate_aliases_for_multi_api_type(
        APIAlias.ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
        APIEntity.API_TYPE_METHOD, APIEntity.API_TYPE_CONSTRUCTOR)

    fuller.start_generate_aliases_for_multi_api_type(
        APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE,
        APIEntity.API_TYPE_CONSTRUCTOR, APIEntity.API_TYPE_METHOD)

    fuller.start_generate_aliases_for_multi_api_type(
        APIAlias.ALIAS_TYPE_SIMPLE_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE,
        APIEntity.API_TYPE_METHOD, APIEntity.API_TYPE_CONSTRUCTOR)

    fuller.start_generate_aliases_for_multi_api_type(
        APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE,
        APIEntity.API_TYPE_METHOD, APIEntity.API_TYPE_CONSTRUCTOR)
    fuller.start_generate_aliases_for_multi_api_type(
        APIAlias.ALIAS_TYPE_SIMPLE_PARENT_API_NAME_WITH_SIMPLE_NAME,
        APIEntity.API_TYPE_ENUM_CONSTANTS, APIEntity.API_TYPE_FIELD, APIEntity.API_TYPE_INTERFACE,
        APIEntity.API_TYPE_EXCEPTION, APIEntity.API_TYPE_PACKAGE, APIEntity.API_TYPE_ANNOTATION,
        APIEntity.API_TYPE_ERROR)

    fuller.start_generate_aliases_for_api_type(
        APIAlias.ALIAS_TYPE_ANNOTATION_REFERENCE,
        APIEntity.API_TYPE_ANNOTATION)

    fuller = APIAliasesTableFuller(commit_step=500)
    fuller.start_generate_aliases_for_multi_api_type(
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
    fuller.start_generate_aliases_for_multi_api_type(
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

    fuller.start_generate_aliases_for_multi_api_type(
        APIAlias.ALIAS_TYPE_VALUE_ALIAS,
        APIEntity.API_TYPE_EXCEPTION_CONDITION,
        APIEntity.API_TYPE_PARAMETER,
        APIEntity.API_TYPE_RETURN_VALUE,

    )
