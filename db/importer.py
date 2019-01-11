from engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from model import KnowledgeTableColumnMapRecord, KnowledgeTableRowMapRecord, APIHTMLText
from model_factory import KnowledgeTableFactory
from shared.logger_util import Logger


class APIHTMLTextImport:
    """
    import the API HTML from one column of one table
    """

    def __init__(self, table, primary_key_name, html_column, html_text_type, session=None, commit_step=5000):
        self.table = table
        self.primary_key_name = primary_key_name
        self.html_column = html_column
        self.html_text_type = html_text_type
        self.commit_step = commit_step
        self.logger_file_name = "import_html_for_" + self.table
        self.logger = None
        self.session = session
        self.api_html_table = None
        self.api_knowledge_table = None
        self.data_source_knowledge_table = None

    def start_import(self):
        self.logger = Logger(self.logger_file_name).get_log()
        if not self.session:
            self.session = EngineFactory.create_session()
        self.init_knowledge_table()

        cur = ConnectionFactory.create_cursor_by_knowledge_table(self.data_source_knowledge_table)

        select_sql = "select {primary_key_name},{html_column} from {table}".format(
            primary_key_name=self.primary_key_name,
            html_column=self.html_column, table=self.table)
        cur.execute(select_sql)
        data_list = cur.fetchall()
        result_tuples = []
        for i in range(0, len(data_list)):
            row_data = data_list[i]
            primary_key = row_data[0]
            html_text = row_data[1]

            if KnowledgeTableColumnMapRecord.exist_import_record(session=self.session,
                                                                 start_knowledge_table=self.data_source_knowledge_table,
                                                                 end_knowledge_table=self.api_html_table,
                                                                 start_row_id=primary_key,
                                                                 start_row_name=self.html_column):
                self.logger.info("%d has been import to new table", primary_key)
                continue
            api_html_text = self.create_from_one_row_data(primary_key, html_text)

            if api_html_text:
                api_html_text = api_html_text.create(self.session, autocommit=False)
                result_tuples.append((api_html_text, primary_key))
            else:
                self.logger.warn("None api_html_text fot %s", str(row_data))
                continue

            if len(result_tuples) > self.commit_step:
                self.commit_to_server_for_column_map(map_tuples=result_tuples)
                result_tuples = []
        self.commit_to_server_for_column_map(map_tuples=result_tuples)
        self.logger.info("import api html completed!")
        cur.close()

    def init_knowledge_table(self):
        self.api_html_table = KnowledgeTableFactory.get_api_html_table(self.session)
        self.api_knowledge_table = KnowledgeTableFactory.get_api_entity_table(self.session)
        self.data_source_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(self.session, self.table)

    def create_from_one_row_data(self, primary_key, html_text):

        new_primary_id_for_api = self.get_api_new_primary_key_by_old_primary_key(old_primary_id=primary_key)

        api_html_text = self.create_api_html_text_html_entity(api_id=new_primary_id_for_api, html_text=html_text)

        return api_html_text

    def get_api_new_primary_key_by_old_primary_key(self, old_primary_id):
        new_primary_id_for_api = KnowledgeTableRowMapRecord.get_end_row_id(session=self.session,
                                                                           start_knowledge_table=self.data_source_knowledge_table,
                                                                           end_knowledge_table=self.api_knowledge_table,
                                                                           start_row_id=old_primary_id)

        if new_primary_id_for_api is None:
            self.logger.error("no new_primary_id_for_api for old_primary_id=%d", old_primary_id)
            return None
        else:
            self.logger.info("old_primary_id=%d -> new_primary_id_for_api =%d", old_primary_id, new_primary_id_for_api)
            return new_primary_id_for_api

    def create_api_html_text_html_entity(self, api_id, html_text):
        if not html_text or not html_text.strip() or html_text=="null":
            self.logger.error("no html_text")
            return None

        if not api_id:
            self.logger.error("no api_id ")
            return None
        api_html_entity = APIHTMLText(api_id=api_id, html=html_text, html_type=self.html_text_type)

        return api_html_entity

    def commit_to_server_for_column_map(self, map_tuples):
        self.logger.info("success=%d", len(map_tuples))
        try:
            self.session.commit()

            for (relation, old_id) in map_tuples:
                record = KnowledgeTableColumnMapRecord(self.data_source_knowledge_table, self.api_html_table, old_id,
                                                       relation.id, self.html_column)
                record.create(self.session, autocommit=False)
            self.session.commit()
        except Exception:
            self.logger.exception("commit_to_server_for_column_map")
