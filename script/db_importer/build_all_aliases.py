from db_importer.entity_alias_builder import EntityAliasesBuilder

if __name__ == "__main__":
    builder = EntityAliasesBuilder()
    builder.init()
    builder.build_aliases()
