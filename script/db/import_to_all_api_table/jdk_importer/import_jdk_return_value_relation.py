from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import KnowledgeTableRowMapRecord, APIEntity, APIRelation
from db.model_factory import KnowledgeTableFactory
from db.util.code_text_process import clean_html_text
from script.db.jdk_importer.import_jdk_return_value_relation_for_method import process_return_type_string, \
    construct_qualified_name_by_full_declaration


def read_return_value_data(cur):
    sql = 'select method_id, full_declaration, return_type, return_string from api_doc.jdk_method where type = "Method"'
    cur.execute(sql)
    return_value_data = cur.fetchall()
    return return_value_data


def import_jdk_return_value_relation(cur, session):
    return_value_data = read_return_value_data(cur)
    total = 0
    type1 = 0
    type2 = 0
    for each in return_value_data:
        total += 1
        method_id = each[0]
        full_declaration = each[1]
        return_type = each[2]
        return_string = each[3]
        return_type = process_return_type_string(return_type)
        qualified_name = construct_qualified_name_by_full_declaration(full_declaration, return_type)
        print("****************")
        print(method_id)
        print(return_type)
        print(full_declaration)
        print(qualified_name)
        if qualified_name is None:
            qualified_name = return_type
        return_string = clean_html_text(return_string)
        parameter_entity = APIEntity.find_by_full_declaration_and_description(session, return_type, return_string)

        jdk_method_knowledge_table = KnowledgeTableFactory.get_jdk_method_table(session)
        api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)
        method_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session, jdk_method_knowledge_table,
                                                                     api_knowledge_table, method_id)
        if parameter_entity is not None and method_entity_id is not None:
            end_api_id = parameter_entity.id
            api_relation_has_return_value = APIRelation(method_entity_id, end_api_id,
                                                        APIRelation.RELATION_TYPE_HAS_RETURN_VALUE)
            api_relation_has_return_value.find_or_create(session, autocommit=False)
            print("------------------------")
            print(api_relation_has_return_value)
            type1 += 1

        if qualified_name is not None and parameter_entity is not None:
            print("+++++++++++++++++++++")
            print(qualified_name)
            class_entity = APIEntity.find_by_qualifier(session, qualified_name)
            if class_entity is not None:
                api_relation_has_type = APIRelation(parameter_entity.id, class_entity.id,
                                                    APIRelation.RELATION_TYPE_RETURN_VALUE_HAS_TYPE)
                api_relation_has_type.find_or_create(session, autocommit=False)
                print("=============================")
                print(api_relation_has_type)
                type2 += 1
    session.commit()
    print("total: " + str(total) + ", type1: " + str(type1) + ", type2: " + str(type2))


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_jdk_importer()
    session = EngineFactory.create_session()
    import_jdk_return_value_relation(cur, session)
