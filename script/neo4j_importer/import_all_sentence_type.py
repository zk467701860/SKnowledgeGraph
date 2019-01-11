from neo4j_importer.api_document_sentence_importer import DocumentSentenceImporter
from skgraph.graph.accessor.graph_accessor import GraphClient


class SentenceTypeImporter:
    importer = DocumentSentenceImporter()
    # import entities automatically
    graph_client = GraphClient(server_number=4)
    importer.init_importer(graph_client=graph_client)
    json_file="sentence_classification_result.json"
    importer.import_sentence_type_from_json(json_file)