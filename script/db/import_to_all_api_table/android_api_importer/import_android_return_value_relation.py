from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity, KnowledgeTableRowMapRecord, APIRelation
from db.model_factory import KnowledgeTableFactory
from db.util.code_text_process import clean_html_text


def read_android_return_value_data(cur):
    sql = "select name, return_value_text, method_id, return_value_url from knowledgeGraph.androidAPI_return_value"
    cur.execute(sql)
    android_return_value_data = cur.fetchall()
    return android_return_value_data


def import_android_return_value_relation(cur, session):
    total = 0
    type1 = 0
    type2 = 0
    return_value_data = read_android_return_value_data(cur)
    for each in return_value_data:
        total += 1
        return_value_name = each[0]
        return_value_text = clean_html_text(each[1])
        method_id = each[2]
        return_value_url = each[3]
        return_value_entity = APIEntity.find_by_full_declaration_and_description(session, return_value_name, return_value_text)
        api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)
        android_method_table = KnowledgeTableFactory.get_android_method_table(session)
        method_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session, android_method_table, api_knowledge_table,
                                                                     method_id)
        qualified_name = ""
        if return_value_url != "":
            qualified_name_list = return_value_url.replace("https://developer.android.google.cn/reference/",
                                                           "").replace(".html", "").split("/")
            for i in range(0, len(qualified_name_list)):
                if i == 0:
                    qualified_name += qualified_name_list[i]
                else:
                    qualified_name += ("." + qualified_name_list[i])
        else:
            qualified_name = return_value_name
        return_value_class = session.query(APIEntity).filter_by(qualified_name=qualified_name).first()
        if return_value_entity is not None and method_entity_id is not None:
            type1 += 1
            api_relation_has_return_value = APIRelation(method_entity_id, return_value_entity.id, APIRelation.RELATION_TYPE_HAS_RETURN_VALUE)
            api_relation_has_return_value.find_or_create(session, autocommit=False)
        if return_value_entity is not None and return_value_class is not None:
            type2 += 1
            api_relation_has_type = APIRelation(return_value_entity.id, return_value_class.id, APIRelation.RELATION_TYPE_RETURN_VALUE_HAS_TYPE)
            api_relation_has_type.find_or_create(session, autocommit=False)
    session.commit()
    print(total)
    print(type1)
    print(type2)


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_android_importer()
    session = EngineFactory.create_session()
    import_android_return_value_relation(cur, session)