from unittest import TestCase

from qa.new_qa.qa_system import QuestionAnswerSystem


class TestQuestionSolverForQueryLibraryWithFunction(TestCase):
    def test_get_answer_collection(self):
        test_case_list = [
            ("which library can parse json", 10),
            ("which library can analysis java code", 10),
            ("which library can do machine learning", 10),

        ]
        qa_system = QuestionAnswerSystem()

        for question_text, size in test_case_list:
            print(question_text)
            answer_collection = qa_system.full_answer(question_text=question_text)
            print(answer_collection)
            self.assertEqual(answer_collection.size(), size)
            print(answer_collection.parse_json())
