# -*- coding:utf8 -*-

from skgraph.qa.candidate_answer_generator import CandidateAnswerSetGenerator
from skgraph.qa.question_analyzer import QuestionAnalyzer
from skgraph.qa.question_answer_system import OldQuestionAnswerSystem
from skgraph.qa.question_preprossor import QuestionPreprossor


## todo: test question answer system in here


def get_candidate_answer(question_text):
    question = question_preprossor.preprosse_question(question_text=question_text)
    question = question_analyzer.analyze_question(question=question)
    question.print_to_console()
    candidate_answer_set = candidate_answer_generator.generate_candidate_answer_set(question=question)
    return candidate_answer_set


def test_qa():
    system = OldQuestionAnswerSystem()
    answer_set = system.fake_full_answer(question_text='What is java')
    print len(answer_set.answer_list)
    # 根据功能查询实体属性描述
    # answer_set = system.full_answer(question_text='what class can perform data collection in java?')
    # answer_set = system.full_answer(question_text='What api can achieve file read and write function?')
    # answer_set = system.full_answer(question_text="I want to know what class can perform data collection in java")

    # 根据相似查询实体名字
    # answer_set = system.full_answer(question_text='what list is similar to thread in c++')
    # answer_set = system.full_answer(question_text='I want to know what list is similar to thread in c++')

    # 根据线程安全查询实体名字
    # answer_set = system.full_answer(question_text='Which list is non thread safe in java?')
    # answer_set = system.full_answer(question_text='I want to know which list is non thread safe in java')
    # answer_set = system.full_answer(question_text='Stringbuilder and Stringbuffer, which is threadsafety in java?')

    # 根据版本查询实体属性描述
    # answer_set = system.full_answer(question_text='Why can not I use InvalidateChild method of android.view.ViewGroup class in api level 26 in android?')

    # 根据实体查询实体描述。
    # answer_set = system.full_answer(question_text="how can I use Stringbuilder?")

    # 单纯通过关键字搜索实体名字
    # answer_set = system.full_answer(question_text='What is cpu')
    # answer_set = system.full_answer(question_text='What is java')
    # answer_set = system.full_answer(question_text="What is stringBuilder in java?")
    # answer_set = system.full_answer(question_text="I want to know thread of java")
    # answer_set = system.full_answer(question_text="Could you tell me what is string?")
    # answer_set = system.full_answer(question_text="The question is what is cpu")
    # answer_set = system.full_answer(question_text='c++ developer')
    # answer_set = system.full_answer(question_text="java thread")


if __name__ == '__main__':
    question_preprossor = QuestionPreprossor()
    question_analyzer = QuestionAnalyzer()
    candidate_answer_generator = CandidateAnswerSetGenerator()

    while True:
        question_text = raw_input("input your question here: ")
        if question_text == "q":
            break
        else:
            candidate_answer_set = get_candidate_answer(question_text)
            if candidate_answer_set:
                candidate_answer_set.print_to_console()
