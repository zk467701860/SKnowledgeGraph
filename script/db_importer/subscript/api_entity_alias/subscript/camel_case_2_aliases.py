from db.alias_util import APIAliasesTableFuller
from db.model import APIAlias, APIEntity

if __name__ == "__main__":
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
