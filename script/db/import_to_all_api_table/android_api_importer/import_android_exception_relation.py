from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity, KnowledgeTableRowMapRecord, APIRelation
from db.model_factory import KnowledgeTableFactory


def read_exception_data(cur):
    sql = 'SELECT name, throw_text, method_id, throw_url FROM knowledgeGraph.androidAPI_throw where name != "" and throw_url != "" and name like "%Exception%";'
    cur.execute(sql)
    android_exception_data = cur.fetchall()
    return android_exception_data


def import_android_exception_relation(cur, session):
    total = 0
    type1 = 0
    type2 = 0
    exception_data = read_exception_data(cur)
    for each in exception_data:
        total += 1
        exception_name = each[0]
        exception_text = each[1].replace("\n", '').replace("           ", '').replace("     ", '').replace("  ", '').replace("   ", '')
        exception_entity = APIEntity.find_by_full_declaration_and_description(session, exception_name, exception_text)
        method_id = each[2]
        api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)
        android_method_table = KnowledgeTableFactory.get_android_method_table(session)
        method_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session, android_method_table, api_knowledge_table, method_id)
        exception_url = each[3]
        qualified_name_list = exception_url.replace("https://developer.android.google.cn/reference/", '').replace(".html", "").split("/")
        qualified_name = ""
        for i in range(0, len(qualified_name_list)):
            if i == 0:
                qualified_name += qualified_name_list[i]
            else:
                qualified_name += ("." + qualified_name_list[i])
        print(qualified_name)
        exception_class = session.query(APIEntity).filter_by(qualified_name=qualified_name).first()

        if exception_entity is not None and method_entity_id is not None:
            api_relation_has_exception = APIRelation(method_entity_id, exception_entity.id, APIRelation.RELATION_TYPE_HAS_EXCEPTION)
            api_relation_has_exception.find_or_create(session, autocommit=False)
            type1 += 1
        if exception_entity is not None and exception_class is not None:
            api_relation_has_type = APIRelation(exception_entity.id, exception_class.id, APIRelation.RELATION_TYPE_EXCEPTION_HAS_TYPE)
            api_relation_has_type.find_or_create(session, autocommit=False)
            type2 += 1
    session.commit()
    print(total)
    print(type1)
    print(type2)


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_android_importer()
    session = EngineFactory.create_session()
    import_android_exception_relation(cur, session)