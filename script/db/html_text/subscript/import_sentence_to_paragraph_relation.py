from db_importer.api_text_paragraph import ParagraphSplitterForDocument

if __name__ == "__main__":
    output_file = "paragraph_data.txt"
    paragraph_splitter = ParagraphSplitterForDocument()
    paragraph_splitter.init()
    # paragraph_splitter.start_split_paragraph(output_file=output_file)
    # paragraph_splitter.import_paragraph_data_from_json_file(paragraph_json_file=output_file)
    paragraph_splitter.import_sentence_to_paragraph_relation_from_json_file(paragraph_json_file=output_file)
