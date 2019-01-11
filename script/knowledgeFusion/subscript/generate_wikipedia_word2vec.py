# !/usr/bin/python
# -*-coding:utf-8-*-

from fusion.entity_vector_computer import EntityVectorGenerator

if __name__ == "__main__":
    generator = EntityVectorGenerator()
    generator.init()
    generator.start_generate_wikipedia_vector()
