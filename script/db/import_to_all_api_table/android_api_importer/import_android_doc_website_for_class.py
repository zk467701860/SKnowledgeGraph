from db.engine_factory import EngineFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity, APIRelation, APIDocumentWebsite
from db.model_factory import KnowledgeTableFactory

session = EngineFactory.create_session()
android_class_knowledge_table = KnowledgeTableFactory.get_android_class_table(session)
api_entity_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)


def get_android_class_data():
    class_id_list = []
    android_class_data = KnowledgeTableRowMapRecord.get_transformed_table_data(session, android_class_knowledge_table, api_entity_knowledge_table)
    for each in android_class_data:
        # print each.end_row_id
        class_id_list.append(each.end_row_id)
    return class_id_list


def construct_android_class_ur(api_entity):
    url = ""
    url_prefix = "https://developer.android.com/reference/"
    qualified_class_name = api_entity.qualified_name
    package_id = APIRelation.get_end_id_by_start_id_and_relation_type(session, api_entity.id, APIRelation.RELATION_TYPE_BELONG_TO)[0]
    if qualified_class_name is not None and package_id is not None:
        print package_id
        parent = APIEntity.find_by_id(session, package_id)
        qualified_package_name = parent.qualified_name
        if qualified_package_name is not None:
            print "-----------------------------------"
            print qualified_package_name, " ", qualified_class_name
            class_name = qualified_class_name.replace(qualified_package_name, "")
            class_name = class_name[1:]
            url += url_prefix
            if "." in qualified_package_name:
                name_list = qualified_package_name.split(".")
            else:
                name_list = [qualified_package_name]
            for name in name_list:
                url += (name + "/")
            url += class_name
            print url
    return url


def import_android_doc_website_for_class():
    class_id_list = get_android_class_data()
    if class_id_list is not None and len(class_id_list) > 0:
        for class_id in class_id_list:
            api_entity = APIEntity.find_by_id(session, class_id)
            if api_entity is not None:
                url = construct_android_class_ur(api_entity)
                if url is not None and url != "":
                    api_document_website = APIDocumentWebsite(api_entity.id, url)
                    api_document_website.find_or_create(session,autocommit=False)
        session.commit()


if __name__ == "__main__":
    import_android_doc_website_for_class()