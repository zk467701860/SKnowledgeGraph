import nltk

from db.engine_factory import EngineFactory
from db.model import APIHTMLText, DocumentText, DocumentSourceRecord, DocumentSentenceText, SentenceToAPIEntityRelation, \
    DocumentParagraphText
from db.model_factory import KnowledgeTableFactory
from db.util.code_text_process import clean_html_text
from db_importer.api_text_paragraph import ParagraphSplitterForDocument


class APITextProcessPipeline:
    def __init__(self):
        self.session = None

    def init(self):
        self.session = EngineFactory.create_session()

    def start_clean_html(self):
        # step 1
        session = self.session
        api_html_text_list = session.query(APIHTMLText).filter_by(clean_text=None).all()
        count = 0
        step = 5000
        for api_html_text in api_html_text_list:
            api_html_text.clean_text = clean_html_text(api_html_text.html)
            count = count + 1
            if count > step:
                session.commit()
                count = 0
        session.commit()

    def import_doc_from_api_html_table(self):
        # step 2: api html->doc
        session = self.session
        api_html_knowledge_table = KnowledgeTableFactory.find_knowledge_table_by_name(session,
                                                                                      APIHTMLText.__tablename__)
        html_text_list = session.query(APIHTMLText).filter_by(
            html_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION).all()

        result_tuples = []
        for html_text in html_text_list:
            if DocumentSourceRecord.exist_import_record(session, api_html_knowledge_table.id, html_text.id):
                print("%d has been import to new table", (html_text.id,))
                continue

            clean_text = html_text.clean_text
            if clean_text is None or clean_text.strip() == "":
                continue

            doc_text = DocumentText(html_text_id=html_text.id, text=clean_text)  # text with no html tags
            doc_text.create(session, autocommit=False)
            result_tuples.append((doc_text, html_text.id))
        session.commit()
        for doc_text, html_text_id in result_tuples:
            record = DocumentSourceRecord(doc_id=doc_text.id, kg_table_id=api_html_knowledge_table.id,
                                          kg_table_primary_key=html_text_id)
            record.create(session, autocommit=False)
        session.commit()

        print("import clean text from html table complete import")

    def check_validation_of_doc_from_html(self):
        # todo: remove duplicate doc or set the valid to 0
        # wangchong have done this
        pass

    def import_sentence_from_doc_table(self):
        # step 3: doc to sentence
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        session = self.session
        document_text_list = session.query(DocumentText).filter_by().all()

        for doc_text in document_text_list:
            text = doc_text.text.strip()
            sentences = tokenizer.tokenize(text)
            for sentence_index, sentence in enumerate(sentences):

                if DocumentSentenceText.exist_import_record(session, doc_id=doc_text.id, sentence_index=sentence_index):
                    print("doc_id=%d sentence index=%d has been import to new table", (doc_text.id, sentence_index))
                    continue
                doc_sentence_text = DocumentSentenceText(doc_id=doc_text.id, sentence_index=sentence_index,
                                                         text=sentence)
                doc_sentence_text.create(session, autocommit=False)
        session.commit()
        print("complete import sentence from document to sentence table")

    def build_paragraph_from_doc_and_import(self):
        # step4: build paragraph and relation
        output_file = "paragraph_data.txt"
        paragraph_splitter = ParagraphSplitterForDocument()
        paragraph_splitter.init()
        paragraph_splitter.start_split_paragraph(output_file=output_file)
        paragraph_splitter.import_paragraph_data_from_json_file(paragraph_json_file=output_file)
        paragraph_splitter.import_sentence_to_paragraph_relation_from_json_file(paragraph_json_file=output_file)

    def build_sentence_to_api_relation(self):
        session = self.session
        all_sentence_list = DocumentSentenceText.get_all_valid_sentences(session)

        count = 0
        step = 5000

        for sentence in all_sentence_list:
            document_text = DocumentText.get_by_id(session=session, id=sentence.doc_id)
            if document_text is None:
                continue
            api_html_text = APIHTMLText.get_by_id(session=session, id=document_text.html_text_id)
            if api_html_text is None:
                continue
            api_id = api_html_text.api_id
            sentence_to_api_relation = SentenceToAPIEntityRelation(sentence_id=sentence.id, api_id=api_id,
                                                                   relation_type=SentenceToAPIEntityRelation.RELATION_TYPE_SOURCE_FROM)
            sentence_to_api_relation.find_or_create(session=session, autocommit=False)
            count = count + 1
            if count > step:
                count = 0
                session.commit()

        session.commit()

    def fix_the_valid_problem_for_paragraph_and_sentence(self):
        session = EngineFactory.create_session()
        # fix the problem of duplicate document
        all_invalid_document_list = session.query(DocumentText).filter_by(valid=0).all()
        count = 0
        step = 3000
        for invalid_document in all_invalid_document_list:
            all_invalid_paragraph_list = session.query(DocumentParagraphText).filter(
                DocumentParagraphText.doc_id == invalid_document.id).all()

            all_invalid_sentence_list = session.query(DocumentSentenceText).filter(
                DocumentSentenceText.doc_id == invalid_document.id).all()

            for paragraph in all_invalid_paragraph_list:
                paragraph.valid = 0
            for sentence in all_invalid_sentence_list:
                sentence.valid = 0

            count = count + 1
            if count > step:
                session.commit()
                count = 0
        session.commit()

        all_paragraph_list = session.query(DocumentParagraphText).filter_by(valid=1).all()
        for paragraph in all_paragraph_list:
            if paragraph.text == None or paragraph.text == "":
                paragraph.valid = 0
                continue
            text = paragraph.text
            text = text.strip()
            if len(text) <= 3 or len(text.split(" ")) <= 2:
                paragraph.valid = 0
        session.commit()

        all_sentence_list = session.query(DocumentSentenceText).filter_by(valid=1).all()
        for sentence in all_sentence_list:
            if sentence.text == None or sentence.text == "":
                sentence.valid = 0
                continue
            text = sentence.text
            text = text.strip()
            if len(text) <= 3 or len(text.split(" ")) <= 2:
                sentence.valid = 0
        session.commit()


if __name__ == "__main__":
    pipeline = APITextProcessPipeline()
    pipeline.init()
    pipeline.start_clean_html()
    pipeline.import_doc_from_api_html_table()
    pipeline.check_validation_of_doc_from_html()
    pipeline.import_sentence_from_doc_table()
    pipeline.build_paragraph_from_doc_and_import()
    pipeline.build_sentence_to_api_relation()
    pipeline.fix_the_valid_problem_for_paragraph_and_sentence()
