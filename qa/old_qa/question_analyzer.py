# -*- coding:utf8 -*-
import os
from question import Question
from nltk import RegexpParser
from nltk.parse.stanford import StanfordDependencyParser
# from pycorenlp import StanfordCoreNLP
# from nltk.parse.stanford import StanfordParser



class QuestionAnalyzer:
    grammar = r"""
                      NP: {<DT|PP\$>?<RB>?<JJ>*<NN><CD>?}   # chunk determiner/possessive, adjectives and noun
                          {<NNP>+}                # chunk sequences of proper nouns
                          {<NNS>+}                # chunk sequences of proper nouns plural
                    """
    path_to_jar = 'model/stanford-parser-3.8.0.jar'
    path_to_models_jar = 'model/stanford-parser-3.8.0-models.jar'

    def __init__(self):
        file_dir = os.path.split(os.path.realpath(__file__))[0]
        # path_to_jar = os.path.join(file_dir, QuestionAnalyzer.path_to_jar)
        # path_to_models_jar = os.path.join(file_dir, QuestionAnalyzer.path_to_models_jar)

        # self.regex_parser = RegexpParser(QuestionAnalyzer.grammar)
        print "done load the regex_parser"

        # self.dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar,
        #                                                  path_to_models_jar=path_to_models_jar)
        print "done load the dependency_parser"
    def analyze_question(self, question):
        '''
        analyze the question,and get the question feature
        :param question: the Question object
        :return: a new Question object after analyze
        '''
        # 'annotators': 'tokenize,ssplit,pos,depparse,parse',
        '''
        nlp = StanfordCoreNLP('http://localhost:9000')
        output = nlp.annotate(question.question_text, properties={
            'annotators': 'depparse',
            'outputFormat': 'text'
        })
        print output
        '''
        result = self.dependency_parser.raw_parse(question.question_text)
        dep = result.next()
        deplist = list(dep.triples())
        print deplist
        target = ''
        priority = 0
        for i in range(0, len(deplist)):
            if deplist[i][1] == 'dobj' and priority < 1:
                target = deplist[i][2][0]
                priority = 1
            elif deplist[i][1] == 'nsubj' and 'NN' in deplist[i][2][1] and priority < 2:
                target = deplist[i][2][0]
                priority = 2
            elif deplist[i][1] == 'det' and priority < 3:
                target = deplist[i][0][0]
                priority = 3
        print 'target:' + target

        result = self.regex_parser.parse(question.tag_question_text)
        print result
        aim = ''
        '''
        for subtree in result.subtrees() :
            if subtree.label() == 'NP' :
                print subtree.leaves()
                print subtree.leaves()[0][0]
                NP.add(subtree.leaves())
        '''
        # What和Which提问
        if 'what' in question.question_text.lower() or 'which' in question.question_text.lower():
            # What is提问，包含针对实体和实体的属性
            if 'what is' in question.question_text.lower() or 'what are' in question.question_text.lower():
                np = ''
                for i in range(2, len(question.tag_question_text)):
                    if question.tag_question_text[i][1] != '.' and question.tag_question_text[i][1] != 'IN' and \
                                    question.tag_question_text[i][1] != 'POS':
                        np += question.tag_question_text[i][0] + ' '
                    else:
                        np = np[:-1]
                        question.NP.append(np)
                        np = ''
                    if i == len(question.tag_question_text) - 1 and np != '':
                        np = np[:-1]
                        question.NP.append(np)
                question.TargetType = 'concept'
                question.query.query_type = 5
            else:
                # 针对线程安全
                if 'thread' in question.question_text and 'safe' in question.question_text:
                    # print 'yes'
                    for subtree in result.subtrees():
                        if subtree.label() == 'NP':
                            np = ''
                            for i in range(0, len(subtree.leaves())):
                                if (subtree.leaves()[i][0] == 'which' or subtree.leaves()[i][0] == 'Which') and \
                                                subtree.leaves()[i][1] == 'JJ':
                                    pass
                                else:
                                    np += subtree.leaves()[i][0] + ' '
                            np = np[:-1]
                            # print 'yes'
                            # print np:
                            question.NP.append(np)
                            if question.TargetType == '':
                                question.TargetType = self.getTargetType(np)
                    question.query.query_type = 3
                else:
                    function = 1
                    for i in range(0, len(question.tag_question_text)):
                        if question.tag_question_text[i][1] != 'VBZ' or question.tag_question_text[i][1] != 'VBP':
                            if 'NN' in question.tag_question_text[i][1] and question.tag_question_text[i][0] != 'safe':
                                question.NP.append(question.tag_question_text[i][0])
                                if question.TargetType == '':
                                    question.TargetType = self.getTargetType(question.tag_question_text[i][0])
                            elif question.tag_question_text[i][1] == 'JJ':
                                if 'thread' not in question.tag_question_text[i][0] and 'safe' not in \
                                        question.tag_question_text[i][0] and 'non' not in question.tag_question_text[i][
                                    0] and 'Which' not in question.tag_question_text[i][0]:
                                    question.JJ.append(question.tag_question_text[i][0])
                                    question.query.query_type = 5
                                    if question.tag_question_text[i][0] == 'similar' and \
                                                    question.tag_question_text[i + 1][0] == 'to':
                                        for j in range(i + 2, len(question.tag_question_text)):
                                            if ('VB' in question.tag_question_text[j][1] or 'NN' in \
                                                    question.tag_question_text[j][1]) and function == 1:
                                                aim += question.tag_question_text[j][0] + ' '
                                            else:
                                                function = 0
                                            if 'NN' in question.tag_question_text[j][1] and function == 0:
                                                if ('IN' in question.tag_question_text[j - 1][1] and 'api' not in
                                                    question.tag_question_text[j][0]):
                                                    question.language = question.tag_question_text[j][0]
                                                else:
                                                    question.NP.append(question.tag_question_text[j][0])
                                        aim = aim[:-1]
                                        question.NP.append(aim)
                                        question.query.query_type = 2
                                        break
                            elif question.tag_question_text[i][1] == 'MD':
                                for j in range(i + 1, len(question.tag_question_text)):
                                    if ('VB' in question.tag_question_text[j][1] or 'NN' in \
                                            question.tag_question_text[j][1] or 'CC' in question.tag_question_text[j][1]) and function == 1:
                                        aim += question.tag_question_text[j][0] + ' '
                                    else:
                                        function = 0
                                    if 'NN' in question.tag_question_text[j][1] and function == 0:
                                        if ('IN' in question.tag_question_text[j - 1][1] and 'api' not in
                                            question.tag_question_text[j][0]):
                                            question.language = question.tag_question_text[j][0]
                                        else:
                                            question.NP.append(question.tag_question_text[j][0])
                                aim = aim[:-1]
                                question.Func.append(aim)
                                question.query.query_type = 1
                                break
                        else:
                            break
                        #print i
        # API废弃提问
        elif 'why' in question.question_text.lower():
            for subtree in result.subtrees():
                if subtree.label() == 'NP':
                    np = ''
                    for i in range(0, len(subtree.leaves())):
                        np += subtree.leaves()[i][0] + ' '
                    np = np[:-1]
                    question.NP.append(np)
                    if question.TargetType == '':
                        question.TargetType = self.getTargetType(np)
                        # print np
            question.query.query_type = 4
        # API使用方法提问
        elif 'how' in question.question_text.lower():
            for subtree in result.subtrees():
                if subtree.label() == 'NP':
                    np = ''
                    for i in range(0, len(subtree.leaves())):
                        np += subtree.leaves()[i][0] + ' '
                    np = np[:-1]
                    question.NP.append(np)
                    if question.TargetType == '':
                        question.TargetType = self.getTargetType(np)
            question.query.query_type = 5
        # 实体发明者提问
        elif 'who' in question.question_text.lower():
            for subtree in result.subtrees():
                if subtree.label() == 'NP':
                    np = ''
                    for i in range(0, len(subtree.leaves())):
                        np += subtree.leaves()[i][0] + ' '
                    np = np[:-1]
                    question.NP.append(np)
                    if question.TargetType == '':
                        question.TargetType = self.getTargetType(np)
            question.query.query_type = 6
        # 实体代码库链接提问
        elif 'where' in question.question_text.lower():
            for subtree in result.subtrees():
                if subtree.label() == 'NP':
                    np = ''
                    for i in range(0, len(subtree.leaves())):
                        np += subtree.leaves()[i][0] + ' '
                    np = np[:-1]
                    question.NP.append(np)
                    if question.TargetType == '':
                        question.TargetType = self.getTargetType(np)
            question.query.query_type = 7
        # 其他句型包括陈述句
        else:
            for subtree in result.subtrees():
                if subtree.label() == 'NP':
                    np = ''
                    for i in range(0, len(subtree.leaves())):
                        np += subtree.leaves()[i][0] + ' '
                    np = np[:-1]
                    question.NP.append(np)
                    if question.TargetType == '':
                        question.TargetType = self.getTargetType(np)
            question.query.query_type = 8
        if target not in question.NP[0]:
            for i in range(0, len(question.NP)):
                if target in question.NP[i]:
                    tempNP = question.NP[i]
                    while i > 0:
                        question.NP[i] = question.NP[i - 1]
                        i -= 1
                    question.NP[i] = tempNP
                    break
        return question

    def getTargetType(self, noun):
        if 'library' in noun:
            return Question.LIBRARY
        elif 'package' in noun:
            return Question.PACKAGE
        elif 'class' in noun:
            return Question.CLASS
        elif 'method' in noun:
            return Question.METHOD
        elif 'api' in noun:
            return Question.METHOD
        else:
            return Question.CONCEPT
