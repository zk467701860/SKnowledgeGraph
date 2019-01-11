# coding=utf-8

from db_importer.general_concept import WikiAliasDBImporter

if __name__ == "__main__":
    importer = WikiAliasDBImporter()
    importer.start_import()
