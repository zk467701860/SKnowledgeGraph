# -*- coding:utf8 -*-
from qa.new_qa.answer_collection import AnswerCollection
from qa.new_qa.intent_analyzer import Question, TemplateIntentAnalyzer, DialogflowIntentAnalyzer, Answer
from qa.new_qa.question_solver import QuestionSolverCollectionFactory
import os

file_dir = os.path.split(os.path.realpath(__file__))[0]
file_name = 'SKnowledge-8e55dec4e266.json'
full_path = os.path.join(file_dir, file_name)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = full_path


class QuestionAnswerSystem:
    def __init__(self):
        self.solver_collection = QuestionSolverCollectionFactory.generate_solver_collection()
        self.template_analyzer = TemplateIntentAnalyzer()
        self.dialogflow_analyzer = DialogflowIntentAnalyzer()
        pass

    def full_answer(self, question_text, top_number=10):
        """
        get answer collection for the question
        :param question_text: question text
        :return:  a full answer collection
        """
        question = Question(question_text)
        print(question_text)
        question_with_intent = self.template_analyzer.generate_question_with_intent(question)
        if question_with_intent is None:
            question_with_intent = self.dialogflow_analyzer.generate_question_with_intent(question)
        answer_collection = self.solver_collection.solve_by_solvers(question_with_intent)
        if answer_collection:
            answer_collection = answer_collection.get_top_answers(top_number=top_number)
        else:
            answer_collection = AnswerCollection()
        if len(answer_collection.answer_list) == 0:
            answer_collection.answer_type = AnswerCollection.ANSWER_TYPE_DEFAULT
            text = "I can't answer this quesion!"
            answer = Answer(answer_text=text, score=1.0, node=None)
            answer_collection.add(answer)

        return answer_collection
