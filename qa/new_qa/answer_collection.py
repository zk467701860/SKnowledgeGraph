class AnswerCollection:
    ANSWER_TYPE_DEFAULT = 0
    ANSWER_TYPE_SINGLE = 1
    ANSWER_TYPE_LIST = 2

    def __init__(self, answer_type=ANSWER_TYPE_DEFAULT, answer_list=None):
        if answer_list is None:
            answer_list = []
        self.answer_type = answer_type
        self.answer_list = answer_list

    def sort(self):
        self.answer_list.sort(key=lambda x: x.score, reverse=True)

    def add(self, answer):
        if answer not in self.answer_list:
            self.answer_list.append(answer)

    def size(self):
        return len(self.answer_list)

    def __repr__(self):
        return '<AnswerCollection: collection=%r>' % (self.answer_list,)

    def get_top_answers(self, top_number):
        self.sort()
        filter_answer_list = self.answer_list[:top_number]
        return AnswerCollection(answer_type=self.answer_type, answer_list=filter_answer_list)

    def parse_json(self):
        answer_list = [answer.parse_json() for answer in self.answer_list]
        return {
            'answer_type': self.answer_type,
            'answer_list': answer_list
        }