class QuestionTemplate():
    WHAT_IS_LIKE_QUESTION=5
    def __init__(self):
        self.template_type=0
        self.answer_entity_type = "unknown"


class WhatIsQuestionTemplate(QuestionTemplate):
    def __init__(self, start_entity_name):
        QuestionTemplate.__init__(self)
        self.template_type = QuestionTemplate.WHAT_IS_LIKE_QUESTION
        self.start_entity_name = start_entity_name
        self.query_relation = ["is", "instance of", "subclass of"]
        self.query_property = ["description", "summary", "name"]

