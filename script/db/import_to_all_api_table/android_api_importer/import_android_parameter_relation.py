from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from db.model import APIEntity, APIRelation, KnowledgeTableRowMapRecord
from db.model_factory import KnowledgeTableFactory
from script.db.import_to_all_api_table.android_api_importer.import_android_parameter import get_simple_parameter_list


def read_parameter_data_from_codehub(session):
    return session.query(APIEntity).filter_by(api_type=APIEntity.API_TYPE_PARAMETER, short_description=None)


def read_parameter_data_from_knowledgegraph(cur):
    sql = 'select id, method_name, full_declaration from knowledgeGraph.androidAPI_method where type like "%method%"'
    cur.execute(sql)
    parameter_data = cur.fetchall()
    return parameter_data


def import_parameter_has_type_relation(session):
    parameter_data_from_codehub = read_parameter_data_from_codehub(session)
    for each in parameter_data_from_codehub:
        # print(each.qualified_name)
        qualified_type = each.qualified_name.split(" ")[0]
        print(qualified_type)
        type_entity = APIEntity.find_by_qualifier(session, qualified_type)
        if type_entity is not None:
            # print(type_entity.id)
            api_relation_has_type = APIRelation(each.id, type_entity.id, APIRelation.RELATION_TYPE_PARAMETER_HAS_TYPE)
            api_relation_has_type.find_or_create(session, autocommit=False)
    session.commit()


def import_parameter_has_parameter_relation(cur, session):
    parameter_data_from_knowledgegraph = read_parameter_data_from_knowledgegraph(cur)
    for each in parameter_data_from_knowledgegraph:
        method_id = each[0]
        full_declaration = each[2]
        simple_parameter_list = get_simple_parameter_list(full_declaration)
        if simple_parameter_list is not None:
            for i in range(0, len(simple_parameter_list)):
                simple_parameter_list[i] = simple_parameter_list[i].replace("[]", "").replace("...", "").strip()
                parameter_entity = APIEntity.find_by_full_declaration_and_description(session, simple_parameter_list[i], None)
                api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(session)
                android_method_table = KnowledgeTableFactory.get_android_method_table(session)
                method_entity_id = KnowledgeTableRowMapRecord.get_end_row_id(session, android_method_table,
                                                                             api_knowledge_table,
                                                                             method_id)
                if parameter_entity is not None and method_entity_id is not None:
                    api_relation_has_parameter = APIRelation(method_entity_id, parameter_entity.id, APIRelation.RELATION_TYPE_HAS_PARAMETER)
                    api_relation_has_parameter.find_or_create(session, autocommit=False)
    session.commit()


def import_android_parameter_relation(cur, session):
    import_parameter_has_type_relation(session)
    import_parameter_has_parameter_relation(cur, session)


if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_android_importer()
    session = EngineFactory.create_session()
    import_android_parameter_relation(cur, session)
