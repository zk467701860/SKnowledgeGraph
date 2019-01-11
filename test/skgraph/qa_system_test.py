from skgraph.qa.question_answer_system import OldQuestionAnswerSystem

if __name__ == "__main__":
    system = OldQuestionAnswerSystem()
    while True:
        question = raw_input("input your question here: ")
        if question == "q":
            break
        answer_set = system.full_answer(question_text=question)
        # answer_set = system.full_answer(question_text='What list is similar to thread in c++?')
        # answer_set = system.full_answer(question_text='What class can perform data collection in java?')
        # answer_set = system.full_answer(question_text='which list is non thread safe in java?')
        # answer_set = system.full_answer(question_text='Why can not I use InvalidateChild method of android.view.ViewGroup class in api level 26 in android?')
        # answer_set = system.full_answer(question_text='What is cpu?')
        # answer_set = system.full_answer(question_text='c++ developer')
        # answer_set = system.full_answer(question_text="What is stringBuilder in java?")
        # answer_set = system.full_answer(question_text="I want to know thread of java")
        # answer_set = system.full_answer(question_text="c++ developer")
        # answer_set = system.full_answer(question_text='Which api can parse XML in Java')
