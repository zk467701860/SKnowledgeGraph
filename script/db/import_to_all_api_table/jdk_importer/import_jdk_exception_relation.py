from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity, APIRelation
from db.model_factory import KnowledgeTableFactory
from db.util.code_text_process import clean_html_text


def read_jdk_exception_data(cur):
    sql = "select name, method_id, description from api_doc.jdk_exception"
    cur.execute(sql)
    jdk_exception_data = cur.fetchall()
    return jdk_exception_data


def get_simple_exception_name_list(session):
    result = []
    exception_data = session.query(APIEntity).filter_by(api_type=APIEntity.API_TYPE_EXCEPTION).all()
    for each in exception_data:
        id = each.id
        qualified_name = each.qualified_name
        name_list = qualified_name.split(".")
        simple_exception_name = name_list[-1]
        temp = {"id": id, "simple_exception_name": simple_exception_name}
        result.append(temp)
    return result


def get_exception_id_by_simple_name(simple_exception_name_list, simple_exception_name):
    if simple_exception_name is not None and simple_exception_name_list is not None:
        for each in simple_exception_name_list:
            if each["simple_exception_name"] == simple_exception_name:
                return each["id"]
    return None


def import_jdk_exception_relation(cur, session):
    jdk_exception_data = read_jdk_exception_data(cur)
    simple_exception_name_list = get_simple_exception_name_list(session)
    total = 0
    type1 = 0
    type2 = 0
    for each in jdk_exception_data:
        total += 1
        name = each[0]
        method_id = each[1]
        description = each[2]
        description = clean_html_text(description)
        exception_entity = APIEntity.find_by_full_declaration_and_description(session, name, description)
        jdk_method_knowledge_table = KnowledgeTableFactory.get_jdk_method_table(session)
        api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)
        method_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session, jdk_method_knowledge_table,
                                                                     api_knowledge_table, method_id)
        if exception_entity is not None and method_entity_id is not None:
            type1 += 1
            api_relation_has_exception = APIRelation(method_entity_id, exception_entity.id, APIRelation.RELATION_TYPE_HAS_EXCEPTION)
            api_relation_has_exception.find_or_create(session, autocommit=False)
            print("------------------------")
            print(api_relation_has_exception)

        if exception_entity is not None and name is not None:
            type2 += 1
            exception_id = get_exception_id_by_simple_name(simple_exception_name_list, name)
            if exception_id is not None:
                api_relation_has_type = APIRelation(exception_entity.id, exception_id, APIRelation.RELATION_TYPE_EXCEPTION_HAS_TYPE)
                api_relation_has_type.find_or_create(session, autocommit=False)
                print("=============================")
                print(api_relation_has_type)
    session.commit()
    print("total: " + str(total) + ", type1: " + str(type1) + ", type2: " + str(type2))


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_jdk_importer()
    session = EngineFactory.create_session()
    import_jdk_exception_relation(cur, session)