from neo4j_importer.api_document_sentence_importer import DocumentSentenceImporter
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    importer = DocumentSentenceImporter()
    # import entities automatically
    graph_client = GraphClient(server_number=4)
    importer.init_importer(graph_client=graph_client)
    importer.start_import_all_valid_sentences()
    # current all sentences will be import to NEO4J, after the result of sentence classification got, we will delete all the Others sentences
    # todo, delete sentence in neo4j that classify as Others

    importer.start_import_all_sentence_to_api_entity_relation()
