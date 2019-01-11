from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from script.db.jdk_importer.import_jdk_exception_relation import import_jdk_exception_relation
from script.db.jdk_importer.import_jdk_parameter_relation import import_jdk_parameter_relation
from script.db.jdk_importer.import_jdk_return_value_relation import import_jdk_return_value_relation

if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_jdk_importer()
    session = EngineFactory.create_session()
    import_jdk_parameter_relation(cur, session)
    import_jdk_return_value_relation(cur, session)
    import_jdk_exception_relation(cur, session)
