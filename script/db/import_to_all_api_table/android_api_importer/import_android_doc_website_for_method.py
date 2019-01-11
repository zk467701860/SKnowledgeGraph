from db.engine_factory import EngineFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity, APIRelation, APIDocumentWebsite
from db.model_factory import KnowledgeTableFactory

session = EngineFactory.create_session()
android_method_knowledge_table = KnowledgeTableFactory.get_android_method_table(session)
api_entity_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)


def get_android_method_data():
    method_id_list = []
    android_method_data = KnowledgeTableRowMapRecord.get_transformed_table_data(session, android_method_knowledge_table, api_entity_knowledge_table)
    for each in android_method_data:
        method_id_list.append(each.end_row_id)
    return method_id_list


def construct_android_method_url(api_entity):
    url = ""
    if api_entity is not None:
        class_id = APIRelation.get_end_id_by_start_id_and_relation_type(session, api_entity.id,
                                                                        APIRelation.RELATION_TYPE_BELONG_TO)[0]
        qualified_method_name = api_entity.qualified_name
        if class_id is not None and qualified_method_name is not None:
            class_document_website_list = APIDocumentWebsite.get_document_website_list_by_api_id(session, class_id)
            class_document_website = ""
            if class_document_website_list is not None:
                for each in class_document_website_list:
                    print "-----------------------------"
                    print each[0]
                    website = each[0]
                    if "https://developer.android.com/reference/" in website:
                        class_document_website = website
                        break
            parent = APIEntity.find_by_id(session, class_id)
            qualified_class_name = parent.qualified_name
            method_name = qualified_method_name.replace(qualified_class_name, "", 1)
            method_name = method_name[1:]
            if "," in method_name:
                method_name = method_name.replace(",", ",%20")
            url = class_document_website + "#" + method_name
            print url
    return url


def import_android_doc_website_for_method():
    method_id_list = get_android_method_data()
    if method_id_list is not None and len(method_id_list) > 0:
        for method_id in method_id_list:
            api_entity = APIEntity.find_by_id(session, method_id)
            if api_entity is not None:
                url = construct_android_method_url(api_entity)
                if url is not None and url is not "":
                    api_document_website = APIDocumentWebsite(api_entity.id, url)
                    api_document_website.find_or_create(session, autocommit=False)
        session.commit()


if __name__ == "__main__":
    import_android_doc_website_for_method()