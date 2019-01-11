from neo4j_importer.domain_entity_importer import DomainEntityImporter
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    importer = DomainEntityImporter()
    graph_client = GraphClient(server_number=4)

    importer.init_importer(graph_client=graph_client)
    importer.start_import_all_domain_entity_extract_by_domain_entity_step(start_domain_entity_id=1961420,end_domain_entity_id=1981420)
