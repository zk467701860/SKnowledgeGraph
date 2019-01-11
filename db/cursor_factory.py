import MySQLdb


class ConnectionFactory:
    @staticmethod
    def create_cursor_for_jdk_importer():
        # todo fix this problem by remove the MySQLdb denpendency
        conn = MySQLdb.connect(
            host='10.131.252.160',
            port=3306,
            user='root',
            passwd='root',
            db='api_doc',
            charset="utf8"
        )
        cur = conn.cursor()
        return cur
        # return None

    @staticmethod
    def create_cursor_by_knowledge_table(knowledge_table):
        conn = MySQLdb.connect(
            host=knowledge_table.ip,
            port=3306,
            user='root',
            passwd='root',
            db=knowledge_table.schema,
            charset="utf8"
        )
        cur = conn.cursor()
        return cur

    @staticmethod
    def create_cursor_for_android_importer():
        conn = MySQLdb.connect(
            host='10.141.221.75',
            port=3306,
            user='root',
            passwd='root',
            db='knowledgeGraph',
            charset="utf8"
        )
        cur = conn.cursor()
        return cur

    @staticmethod
    def create_cursor_and_conn():
        # todo fix this problem by remove the MySQLdb denpendency
        conn = MySQLdb.connect(
            host='10.131.252.160',
            port=3306,
            user='root',
            passwd='root',
            db='api_doc',
            charset="utf8"
        )
        cur = conn.cursor()
        return cur, conn
