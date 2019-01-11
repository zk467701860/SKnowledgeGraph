from db_importer.general_concept import WikiAliasDBImporter
from neo4j_importer.software_related_wikidata_importer import SoftwareRelatedWikidataConceptImporter
from neo4j_importer.wikidata_relation_linker import WDRelationLinker
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    importer = SoftwareRelatedWikidataConceptImporter()
    client = GraphClient(server_number=4)
    importer.init_importer(client=client)

    importer.start_import_annotation_wikidata()
    importer.start_import_all_classify_result()

    linker = WDRelationLinker(graph_client=client)
    linker.start_link()

    importer = WikiAliasDBImporter()
    importer.start_import()
