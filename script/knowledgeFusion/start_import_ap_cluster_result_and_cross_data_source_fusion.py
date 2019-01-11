from fusion.cross_sentence_fusion import APClusterResultDBImporterPipeline
from fusion.cross_source_fusion import CrossDataSourceFusion, CrossDataSourceFusionResultKGImporter
from neo4j_importer.domain_entity_importer import DomainEntityImporter
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    # 1.import cluster result to DB
    pipeline = APClusterResultDBImporterPipeline()
    pipeline.init()
    ap_cluster_result_file = "weight-0.5-depth-0.json"
    pipeline.start_import_entity_and_relation(ap_cluster_result_file)
    print("complete import domain entity to DB")
    # 2.import cluster result to from DB to KG
    importer = DomainEntityImporter()
    graph_client = GraphClient(server_number=4)
    importer.init_importer(graph_client=graph_client)
    importer.clean_kg_by_remove_all_domain_entity()
    importer.start_import_all_domain_entity()
    importer.start_import_all_domain_entity_extract_from_relation()
    print("complete import domain entity to KG")

    # 3.start the fusion between the domain entity and wikipedia entity
    fusion = CrossDataSourceFusion()
    fusion.init()
    link_relation_json = "domain_entity_to_wikidata_link_relation.json"
    fusion.start_fusion_for_domain_entity(link_relation_json)
    importer = CrossDataSourceFusionResultKGImporter()
    importer.start_import_for_domain_entity(link_relation_json)

    # print("complete CrossDataSourceFusion for domain entity and import them to kg")
    # link_relation_json = "api_to_wikidata_link_relation.json"
    # fusion.start_fusion_for_api(link_relation_json)
    # importer = CrossDataSourceFusionResultKGImporter()
    # importer.start_import_for_api_entity(link_relation_json)
    #
    # print("complete CrossDataSourceFusion for api entity and import them to kg")