from db.engine_factory import EngineFactory
from db.model import KnowledgeTable
from db.model_factory import KnowledgeTableFactory

tables_data = KnowledgeTableFactory.tables_data

session = EngineFactory.create_session()

for table in tables_data:
    knowledge_table = KnowledgeTable(ip=table["ip"], schema=table["schema"], table_name=table["table_name"],
                                     description=table["description"])
    knowledge_table = knowledge_table.find_or_create(session)
    print(knowledge_table)
    print(knowledge_table.id)
