from neo4j_importer.software_related_wikidata_importer import SoftwareRelatedWikidataConceptImporter
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    importer = SoftwareRelatedWikidataConceptImporter()
    importer.init_importer(client=GraphClient(server_number=4))

    importer.start_import_annotation_wikidata()
    importer.start_import_all_classify_result()

    # importer.import_wikidata_entity(url="https://en.wikipedia.org/wiki/Japanese_language_and_computers")
    # importer.import_wikipedia_entity(url="https://en.wikipedia.org/wiki/Japanese_language_and_computers")
