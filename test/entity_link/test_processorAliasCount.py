from unittest import TestCase

from entity_link.corpus import ProcessorAliasCount


class TestProcessorAliasCount(TestCase):
    def test_process_alias_2_entity_map(self):
        processor = ProcessorAliasCount()
        input_file = "alias_to_entity_count.json"
        out_put_file = "token_lower_alias_to_entity_count.json"
        processor.process_alias_2_entity_map(input_file, out_put_file)
