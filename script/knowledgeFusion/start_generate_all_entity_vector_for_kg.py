# !/usr/bin/python
# -*-coding:utf-8-*-

from fusion.entity_vector_computer import EntityVectorGenerator

if __name__ == "__main__":
    generator = EntityVectorGenerator()
    generator.init()
    generator.start_generate_wikipedia_vector()
    generator.start_generate_domain_entity_vector()
    generator.start_generate_api_entity_vector()
    generator.start_generate_sentence_vector()
