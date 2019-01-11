from script.db.html_text.start_the_text_import_pipeline import APITextProcessPipeline

if __name__ == "__main__":
    pipeline = APITextProcessPipeline()
    pipeline.init()
    pipeline.fix_the_valid_problem_for_paragraph_and_sentence()
