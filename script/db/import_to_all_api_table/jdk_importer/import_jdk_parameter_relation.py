from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity, KnowledgeTableRowMapRecord, APIRelation
from db.model_factory import KnowledgeTableFactory
from db.util.code_text_process import clean_html_text


def read_parameter_data(cur):
    sql = "select name, method_id, type_string, description, type_class from api_doc.jdk_parameter"
    cur.execute(sql)
    parameter_data = cur.fetchall()
    return parameter_data


def import_jdk_parameter_relation(cur, session):
    parameter_data = read_parameter_data(cur)
    for each in parameter_data:
        if each is not None:
            name = each[0]
            method_id = each[1]
            type_string = each[2]
            description = each[3]
            type_class = each[4]
            full_declaration = type_string + " " + name
            description = clean_html_text(description)
            parameter_entity = APIEntity.find_by_full_declaration_and_description(session, full_declaration, description)
            jdk_method_knowledge_table = KnowledgeTableFactory.get_jdk_method_table(session)
            api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)
            method_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session, jdk_method_knowledge_table, api_knowledge_table, method_id)

            if parameter_entity is not None and method_entity_id is not None:
                end_api_id = parameter_entity.id
                api_relation_has_parameter = APIRelation(method_entity_id, end_api_id, APIRelation.RELATION_TYPE_HAS_PARAMETER)
                print("------------------------")
                print(api_relation_has_parameter)
                api_relation_has_parameter.find_or_create(session, autocommit=False)
            if type_class == 0:
                qualified_class_name = type_string
            else:
                qualified_class_name = get_qualified_class_name(type_class, cur)
            if qualified_class_name is not None and parameter_entity is not None:
                class_entity = APIEntity.find_by_qualifier(session, qualified_class_name)
                if class_entity is not None:
                    api_relation_has_type = APIRelation(parameter_entity.id, class_entity.id, APIRelation.RELATION_TYPE_PARAMETER_HAS_TYPE)
                    print("=============================")
                    print(api_relation_has_type)
                    api_relation_has_type.find_or_create(session, autocommit=False)
    session.commit()


def get_qualified_class_name(type_class, cur):
    if type_class is not None and type_class != 0:
        sql = 'select name from api_doc.jdk_class where class_id = ' + str(type_class)
        cur.execute(sql)
        qualified_class_data = cur.fetchone()
        if qualified_class_data is not None:
            return qualified_class_data[0]
    return None


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_jdk_importer()
    session = EngineFactory.create_session()
    import_jdk_parameter_relation(cur, session)