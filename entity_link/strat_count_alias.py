from entity_link.corpus import ProcessorAliasCount, AliasStatisticsUtil

if __name__=="__main__":
    processor=ProcessorAliasCount()
    new_vocabulary_path = "data/normalize_alias_link.json"
    processor.process_alias_2_entity_map("data/alias_link.json", new_vocabulary_path)
    aliasStatisticsUtil = AliasStatisticsUtil(alias_ngram=True)
    aliasStatisticsUtil.init_vocabulary_from_json(new_vocabulary_path)
    aliasStatisticsUtil.count_occur_from_json("data/html.json")
    final_tsv_path = "data/alias-entity-counts.tsv"
    aliasStatisticsUtil.write_to_tsv(final_tsv_path)
