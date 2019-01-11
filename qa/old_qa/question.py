# -*- coding:utf8 -*-

from query import Query


class Question:
    # following is the TargetType value
    LIBRARY = 'library'
    CLASS = 'class'
    METHOD = 'method'
    PACKAGE = 'package'
    CONCEPT = 'concept'

    def __init__(self, question_text, tag_question_text):
        self.question_text = question_text
        self.tag_question_text = tag_question_text
        self.NP = []  # 表示名词词组
        self.JJ = []  # 表示形容词
        self.Func = []  # 表示功能介绍，一般为动词加名词
        self.TargetType = ''  # 表示目标类型
        self.language = ''
        self.query = Query()

    def get_keywords(self):
        return self.NP + self.Func + self.JJ

    def print_to_console(self):
        print 'NP:  ' + str(len(self.NP))
        for i in range(0, len(self.NP)):
            print self.NP[i]
        print 'Func:  ' + str(len(self.Func))
        for i in range(0, len(self.Func)):
            print self.Func[i]
        print 'JJ:  ' + str(len(self.JJ))
        for i in range(0, len(self.JJ)):
            print self.JJ[i]
        print 'TargetType:  ' + self.TargetType
        print 'language:  ' + self.language
        print 'QueryType:  ' + str(self.query.query_type)
