from neo4j_importer.api_document_sentence_importer import DocumentSentenceImporter
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    importer = DocumentSentenceImporter()
    # import entities automatically
    graph_client = GraphClient(server_number=4)
    importer.init_importer(graph_client=graph_client)
    importer.start_import_all_sentence_to_api_entity_relation()
