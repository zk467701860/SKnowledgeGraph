from unittest import TestCase

from qa.new_qa.intent_analyzer import TemplateGenerator


class TestTemplateMatcher(TestCase):
    def test_get_slot_dict(self):
        matcher_list = TemplateGenerator().generate_all()
        matcher = matcher_list[0]
        test_cases = [
            ("what is Java", {'Entity': 'Java'}),
            ("What is Java", {'Entity': 'Java'}),
            ("how can I do homework", None),
            ("", None),
            ("what are libraries", {'Entity': 'libraries'}),
            ("what is computer science", {'Entity': 'computer science'}),
            ("what is computer science?", {'Entity': 'computer science'}),
            (" what is computer science ", {'Entity': 'computer science'}),
        ]
        for query, right_slot_dict in test_cases:
            slot_dict = matcher.get_slot_dict(query)
            self.assertEqual(slot_dict, right_slot_dict)

    def test_get_slot_dict_for_multiply_matcher(self):
        matcher_list = TemplateGenerator().generate_all()
        matcher_test_data_list = []

        matcher = matcher_list[0]
        test_cases = [
            ("what is Java", {'Entity': 'Java'}),
            ("What is Java", {'Entity': 'Java'}),
            ("how can I do homework", None),
            ("", None),
            ("what are libraries", {'Entity': 'libraries'}),
            ("what is computer science", {'Entity': 'computer science'}),
            ("what is computer science?", {'Entity': 'computer science'}),
            (" what is computer science ", {'Entity': 'computer science'}),
        ]
        matcher_test_data_list.append((matcher, test_cases))

        matcher = matcher_list[1]
        test_cases = [
            ("what is Java", None),
            ("What is Java", None),
            ("how can I do homework", None),
            ("", None),
            ("what are libraries", None),
            ("what is computer science", None),
            ("what is computer science?", None),
            (" what is computer science ", None),
            ("which library can parse Json", {"Function": "parse Json"}),
            ("which library can do machine learning", {"Function": "do machine learning"}),

        ]
        matcher_test_data_list.append((matcher, test_cases))

        for matcher, test_cases in matcher_test_data_list:
            for query, right_slot_dict in test_cases:
                slot_dict = matcher.get_slot_dict(query)
                self.assertEqual(slot_dict, right_slot_dict)

    def test_get_intent(self):
        self.fail()
