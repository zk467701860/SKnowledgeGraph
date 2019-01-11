from db_importer.wiki_classification_result import WikiClassificationResultDBImporter

if __name__ == "__main__":
    importer = WikiClassificationResultDBImporter()
    importer.import_lr_wiki_classification_result(result_json_file_name="lr_result.v2.json")
