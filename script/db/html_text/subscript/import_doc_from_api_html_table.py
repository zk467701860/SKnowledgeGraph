from script.db.html_text.start_the_text_import_pipeline import APITextProcessPipeline

if __name__ == "__main__":
    pipeline = APITextProcessPipeline()
    pipeline.init()
    pipeline.import_doc_from_api_html_table()
