from unittest import TestCase

from qa.new_qa.graph_accessor_for_qa import QAGraphAccessor
from qa.new_qa.intent_analyzer import QuestionWithIntent, TemplateIntentAnalyzer, Question
from qa.new_qa.qa_system import QuestionAnswerSystem
from qa.new_qa.question_solver import QuestionSolverForQuerySingleEntity
from skgraph.graph.accessor.graph_accessor import GraphClient


class TestQuestionSolverForQuerySingleEntity(TestCase):
    def test_get_answer_list(self):
        accessor = QAGraphAccessor(GraphClient())
        solver = QuestionSolverForQuerySingleEntity(graph_accessor=accessor)

        question_text = "What is linux"
        question = Question(question_text)
        analyzer = TemplateIntentAnalyzer()
        question_with_intent = analyzer.generate_question_with_intent(question)
        result = solver.get_answer_collection(question_with_intent)
        self.assertEqual(result.size(), 45)
        print(result)

    def test_full_answer(self):
        test_case_list = [
            ("What is linux", 10),
            ("what is Python", 10),
            ("what is Gson", 3),
            ("what is C++", 10),
            ("what is C", 10),
            ("what is Windows", 10),
            ("what is HTTP", 10),
        ]
        qa_system = QuestionAnswerSystem()

        for question_text, size in test_case_list:
            print(question_text)
            answer_collection = qa_system.full_answer(question_text=question_text)
            print(answer_collection)
            self.assertEqual(answer_collection.size(), size)
            print(answer_collection.parse_json())
