from fusion.cross_source_fusion import CrossDataSourceFusion, CrossDataSourceFusionResultKGImporter

if __name__ == "__main__":
    fusion = CrossDataSourceFusion()
    fusion.init()
    link_relation_json = "domain_entity_link_relation.json"
    fusion.start_fusion_for_domain_entity(link_relation_json)

    importer = CrossDataSourceFusionResultKGImporter()
    importer.start_import_for_domain_entity(link_relation_json)


    # fusion.start_fusion_for_domain_entity(link_relation_json)
    # link_relation_json = "api_entity_link_relation.json"
    # fusion.start_fusion_for_api(link_relation_json)
    # importer.start_import_for_api_entity(link_relation_json)
