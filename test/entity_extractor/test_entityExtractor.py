from unittest import TestCase

from entity_extractor.extractor import EntityExtractor


class TestEntityExtractor(TestCase):
    def test_get_clean_np(self):
        entity_extractor = EntityExtractor()

        test_case_list = [
            ("Activities", "activity"),
            ("an activity", "activity"),
            ("...empty space", "empty space"),
            ("return it", None),
            ("your idea it", "idea"),
            ("your its idea it", "idea"),
            ("activity", "activity"),
            ("code sample", "code sample"),
            ("@ null", "@null"),
            ("", ""),
        ]
        for (question_np, answer_np) in test_case_list:
            clean_np = entity_extractor.get_clean_entity_name_for_string(question_np)
            self.assertEqual(answer_np, clean_np)
            print(question_np, answer_np)

    def test_is_valid_chunk_string(self):
        entity_extractor = EntityExtractor()
        np_list = [
            ("Result.PI_DISABLE_OUTPUT_ESCAPING and Result.PI_ENABLE_OUTPUT_ESCAPING", False),  ## todo fix
            ("RFC 2911 Internet Printing Protocol/1.1", False),  ## todo,fix
            ("super T> accumulator", False),
            ("SyncFactory SyncProvider SyncFactoryException SyncProviderException SyncResolver XmlReader XmlWriter",
             False),
            ("SyncProvider.GRADE_LOCK_WHEN_LOADED // A pessimistic synchronization grade break", False),
            ("PooledConnection ConnectionEvent ConnectionEventListener StatementEvent StatementEventListener", False),
            ("PrintServiceLookup.lookupPrintServices(psInFormat", False),
            ("Programmatic updates--using ResultSet updater methods New data types--interfaces", False),
            ("5.0 SerialDatalink", False),
            ("// more info", False),
            ("Activity", True),
            ("see more http://www.baidu.com", False),
            ('''<style id="labelStyle"> <opaque value="FALSE"/> </style>''', False),
        ]
        for np, valid in np_list:
            print(np)
            self.assertEqual(entity_extractor.is_valid_chunk_string(np), valid)

    def test_extract_clean_entity_name_from_text(self):
        entity_extractor = EntityExtractor()

        entity_list = entity_extractor.extract_clean_entity_name_from_text("Round a double to 2 decimal places")
        print(entity_list)

    def test_extract_single_verb(self):
        entity_extractor = EntityExtractor()
        result = entity_extractor.extract_single_verb("How can I lock a file using java")
        print(result)

    def test_extract_single_verb_all_np(self):
        entity_extractor = EntityExtractor()
        result = entity_extractor.extract_verb_and_entity_name_from_text("How can I lock a file using java")
        print(result)
        result = entity_extractor.extract_verb_and_entity_name_from_text("How to lock a file using java")
        print(result)
