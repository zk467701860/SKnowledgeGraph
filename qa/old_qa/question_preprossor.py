# -*- coding:utf8 -*-

from question import Question
import nltk
from nltk import RegexpParser

class QuestionPreprossor:
    def __init__(self):
        pass

    def preprosse_question(self, question_text):
        '''
        preprosse the question string,and get a question object
        :param question_text: question text
        :return: the Question object
        '''
        # todo complete the QuestionPreprossor
        #增加词性标注
        text = nltk.word_tokenize(question_text)
        tag_text = nltk.pos_tag(text)
        print text
        print tag_text
        process_tag_text = []
        length = len(tag_text)
        i = 0
        is_complex_question = 0
        begin_question = 0
        while i < length :
            threshold = 0
            newtuple = ()
            #print 'Begin    ' + str(i)

            # 找出从句中的实质性问句
            if is_complex_question == 1 or (',' not in question_text and ('what' in question_text.lower() or 'which' in question_text.lower() or 'why' in question_text.lower()) and i == 0 and 'what' not in tag_text[i][0].lower() and 'which' not in tag_text[i][0].lower() and 'why' not in tag_text[i][0].lower()):
                is_complex_question = 1
                if 'what' in tag_text[i][0].lower() or 'which' in tag_text[i][0].lower() or 'why' in tag_text[i][0].lower() :
                    begin_question = 1
                if begin_question == 0 :
                    i += 1
                    continue
                else :
                    if 'api' in tag_text[i][0].lower() or 'library' in tag_text[i][0].lower() or 'package' in tag_text[i][0].lower() or 'class' in tag_text[i][0].lower() or 'method' in tag_text[i][0].lower() :
                        newtuple = (tag_text[i][0], 'NN')
                    else :
                        newtuple = (tag_text[i][0], tag_text[i][1])
                    #process_tag_text.append(newtuple)

            # 将thread safe的词性在不同句式中进行统一
            if i < len(tag_text) - 1 and 'thread' in tag_text[i][0] and 'safe' in tag_text[i + 1][0]:
                # print 'yes'
                newtuple = (tag_text[i][0], 'JJ')
                process_tag_text.append(newtuple)
                newtuple = (tag_text[i + 1][0], 'NN')
                process_tag_text.append(newtuple)
                threshold = 1
            elif 'thread' in tag_text[i][0] and 'safe' in tag_text[i][0] :
                newtuple = ('thread', 'JJ')
                process_tag_text.append(newtuple)
                newtuple = ('safe', 'NN')
                process_tag_text.append(newtuple)
            else :
                #print 'no'
                newtuple = (tag_text[i][0],tag_text[i][1])
                process_tag_text.append(newtuple)
            if threshold == 1 :
                i += 1
            #print 'End   ' + str(i)
            i += 1
        print process_tag_text
        return Question(question_text=question_text,tag_question_text=process_tag_text)

if __name__ == '__main__':
    question_preprossor = QuestionPreprossor()
    question = question_preprossor.preprosse_question("Which list is thread unsafe in java?")
    #print question.question_text
    #print question.tag_question_text
