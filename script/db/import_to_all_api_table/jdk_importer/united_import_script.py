from db.cursor_factory import ConnectionFactory
from db.engine_factory import EngineFactory
from script.db.jdk_importer.import_jdk_exception_condition import import_jdk_exception_condition
from script.db.jdk_importer.import_jdk_parameter import import_jdk_parameter
from script.db.jdk_importer.import_jdk_return_value import import_jdk_return_value

if __name__ == "__main__":
    cur = ConnectionFactory.create_cursor_for_jdk_importer()
    session = EngineFactory.create_session()
    import_jdk_parameter(cur, session)
    import_jdk_return_value(cur, session)
    import_jdk_exception_condition(cur, session)