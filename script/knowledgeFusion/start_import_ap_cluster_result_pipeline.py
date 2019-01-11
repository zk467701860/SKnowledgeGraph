from fusion.cross_sentence_fusion import APClusterResultDBImporterPipeline

if __name__ == "__main__":
    pipeline = APClusterResultDBImporterPipeline()
    pipeline.init()
    ap_cluster_result_file = "threshold-1.6-hierarchy_cluster.json"
    pipeline.start_import_entity_and_relation(ap_cluster_result_file)
