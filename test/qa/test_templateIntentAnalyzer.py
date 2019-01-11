from unittest import TestCase

from qa.new_qa.intent_analyzer import Question, TemplateIntentAnalyzer, Intent


class TestTemplateIntentAnalyzer(TestCase):
    def test_analysis_intent(self):
        question = Question(question_text="what is Java")
        analyzer = TemplateIntentAnalyzer()
        intent = analyzer.analysis_intent(question)
        self.assertEqual(intent.intent_type, Intent.INTENT_TYPE_QUERY_SINGLE_ENTITY)
        self.assertEqual(intent.slot_dict["Entity"], "Java")

    def test_analysis_intent_for_find_library(self):
        question = Question(question_text="which library can parse Json")
        analyzer = TemplateIntentAnalyzer()
        intent = analyzer.analysis_intent(question)
        self.assertEqual(intent.intent_type, Intent.INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION)
        self.assertEqual(intent.slot_dict["Function"], "parse Json")
