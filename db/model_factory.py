from model import APIEntity, APIRelation, LibraryEntity, APIDocumentWebsite, APIAlias, APIBelongToLibraryRelation, \
    KnowledgeTable, KnowledgeTableRowMapRecord, APIHTMLText, PostsRecord, EntityHeat


class KnowledgeTableFactory:
    tables_data = [
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": APIEntity.__tablename__,
         "description": "all java api from differen sources, for unified management"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": EntityHeat.__tablename__,
         "description": "all entity heat"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": APIRelation.__tablename__,
         "description": "all java api relation"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": LibraryEntity.__tablename__,
         "description": "all library from differen sources, for unified management"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": APIDocumentWebsite.__tablename__,
         "description": "the api document websites for one api"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": APIAlias.__tablename__,
         "description": "the api aliases generate form different source"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": APIHTMLText.__tablename__,
         "description": "collect all the html text and cleaned html text for API"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": APIBelongToLibraryRelation.__tablename__,
         "description": "the api belong to libraries"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": KnowledgeTable.__tablename__,
         "description": "the knowledge table itself"},
        {"ip": "10.141.221.73", "schema": "codehub", "table_name": KnowledgeTableRowMapRecord.__tablename__,
         "description": "the row map for different Knowledge Table, save for trace the relation between tables"},
        {"ip": "10.131.252.160", "schema": "api_doc", "table_name": "jdk_library",
         "description": "the different versions of jdk, including 5,6,7,8"},
        {"ip": "10.131.252.160", "schema": "api_doc", "table_name": "jdk_package",
         "description": "the different versions of jdk package including 5,6,7,8"},
        {"ip": "10.131.252.160", "schema": "api_doc", "table_name": "jdk_class",
         "description": "the different versions of jdk package including 5,6,7,8. the class actually contains interface, exception, enum and others"},
        {"ip": "10.131.252.160", "schema": "api_doc", "table_name": "jdk_method",
         "description": "the different versions of jdk package including 5,6,7,8. the methods actually contains interface, exception, enum and others"},
        {"ip": "10.131.252.160", "schema": "api_doc", "table_name": "jdk_parameter",
         "description": "the parameter of jdk method"},
        {"ip": "10.141.221.75", "schema": "knowledgeGraph", "table_name": "androidAPI_package",
         "description": "the method extract from android api document for API 27"},
        {"ip": "10.141.221.75", "schema": "knowledgeGraph", "table_name": "androidAPI_class",
         "description": "the class extract from android api document for API 27"},
        {"ip": "10.141.221.75", "schema": "knowledgeGraph", "table_name": "androidAPI_method",
         "description": "the method extract from android api document for API 27"},
        {"ip": "10.141.221.75", "schema": "knowledgeGraph", "table_name": "androidAPI_support_package",
         "description": "the method extract from android api document for support library"},
        {"ip": "10.141.221.75", "schema": "knowledgeGraph", "table_name": "androidAPI_support_class",
         "description": "the class extract from android api document for support library"},
        {"ip": "10.141.221.75", "schema": "knowledgeGraph", "table_name": "androidAPI_support_method",
         "description": "the method extract from android api document for support library"},
        {"ip": "10.131.252.160", "schema": "stackoverflow", "table_name": PostsRecord.__tablename__,
         "description": "stack_overflow post record"},
    ]

    @staticmethod
    def find_knowledge_table_by_name(session, name):
        table = KnowledgeTableFactory.__get_table_data_by_name(name)
        if table == None:
            return None
        else:
            knowledge_table = KnowledgeTable(ip=table["ip"], schema=table["schema"], table_name=table["table_name"],
                                             description=table["description"])
            knowledge_table = knowledge_table.find_or_create(session)
            return knowledge_table

    @staticmethod
    def __get_table_data_by_name(name):
        for item in KnowledgeTableFactory.tables_data:
            if item["table_name"] == name:
                return item
        return None

    @staticmethod
    def get_jdk_library_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, "jdk_library")

    @staticmethod
    def get_library_entity_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, LibraryEntity.__tablename__)

    @staticmethod
    def get_jdk_package_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, "jdk_package")

    @staticmethod
    def get_api_entity_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, APIEntity.__tablename__)

    @staticmethod
    def get_jdk_class_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, "jdk_class")

    @staticmethod
    def get_api_relation_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, APIRelation.__tablename__)

    @staticmethod
    def get_api_document_website_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, APIDocumentWebsite.__tablename__)

    @staticmethod
    def get_jdk_method_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, "jdk_method")

    @staticmethod
    def get_api_belong_to_library_relation_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, APIBelongToLibraryRelation.__tablename__)

    @staticmethod
    def get_api_html_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, APIHTMLText.__tablename__)

    @staticmethod
    def get_posts_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, PostsRecord.__tablename__)

    @staticmethod
    def get_android_package_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, "androidAPI_package")

    @staticmethod
    def get_android_class_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, "androidAPI_class")

    @staticmethod
    def get_android_method_table(session):
        return KnowledgeTableFactory.find_knowledge_table_by_name(session, "androidAPI_method")
