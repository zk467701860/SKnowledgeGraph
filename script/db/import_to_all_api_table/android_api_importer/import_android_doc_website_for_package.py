from db.engine_factory import EngineFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity, APIDocumentWebsite
from db.model_factory import KnowledgeTableFactory

session = EngineFactory.create_session()
android_package_knowledge_table = KnowledgeTableFactory.get_android_package_table(session)
api_entity_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)


def get_android_package_data():
    package_id_list = []
    android_package_data = KnowledgeTableRowMapRecord.get_transformed_table_data(session, android_package_knowledge_table, api_entity_knowledge_table)
    if android_package_data is not None:
        for each in android_package_data:
            end_row_id = each.end_row_id
            print end_row_id
            package_id_list.append(end_row_id)
    # print android_package_data
    return package_id_list


def construct_android_package_url(api_entity):
    url = ""
    url_prefix = "https://developer.android.com/reference/"
    url_suffix = "package-summary"
    if api_entity is not None:
        qualified_name = api_entity.qualified_name
        if "." in qualified_name:
            name_list = qualified_name.split(".")
        else:
            name_list = [qualified_name]
        url += url_prefix
        for name in name_list:
            url += (name + "/")
        url += url_suffix
    return url


def import_android_doc_website_for_package():
    package_id_list = get_android_package_data()
    if package_id_list is not None and len(package_id_list) > 0:
        for package_id in package_id_list:
            api_entity = APIEntity.find_by_id(session, package_id)
            url = construct_android_package_url(api_entity)
            print url
            if api_entity is not None and url is not "":
                api_document_website = APIDocumentWebsite(api_entity.id, url)
                print api_document_website
                api_document_website.find_or_create(session=session, autocommit=False)
        session.commit()


if __name__ == "__main__":
    import_android_doc_website_for_package()
