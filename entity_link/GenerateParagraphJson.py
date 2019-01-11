# encoding: utf-8
import csv
from bs4 import BeautifulSoup, Comment
from NormalizeUtil import transform_url_to_qualifier
from NormalizeUtil import isLegalAlias
from filter import TextPreprocessor
import re
import json

total_negative_pair = 0
total_entity_pair = 0
can_not_find = 0

def resolve(postid, content, post_list):
    global total_negative_pair
    global can_not_find
    post_dict = {}
    #space_pattern = re.compile('\n')
    punct_pattern = re.compile('\s{2,}')
    #content = punct_pattern.sub(' ', content)
    #print content
    soup = BeautifulSoup(content, "lxml")
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]
    [blockquote.extract() for blockquote in soup('blockquote')]
    for code in soup("code"):
        code_text = code.get_text()
        if not len(code_text.split()) <= 3 and not TextPreprocessor.PATTERN_METHOD.match(code_text):
            code.extract()
            continue
    #content = space_pattern.sub(' ', soup.get_text())
    #print content
    a_list = soup.select('a')
    alias_list = []
    entity_list = []
    for a in a_list:
        if a.get('href'):
            entity = transform_url_to_qualifier(a.get('href'))
            if entity != '':
                #print a
                alias = isLegalAlias(a.get_text().lstrip())
                #print alias
                if alias != '':
                    alias_list.append(alias + '###')
                    a.append('###')
                    entity_list.append(entity)
    #new_content = space_pattern.sub(' ', soup.get_text())
    #print len(alias_list)
    #print '!!!!!!!!!!!!!!'
    #print new_content
    p_list = soup.select('p')
    if len(p_list) > 0:
        total_a = 0
        for p in p_list:
            p_content = p.get_text()
            total_a += p_content.count('###', 0, len(p_content))
        if total_a == len(alias_list):
            paragragh_index = 0
            alias_index = 0
            error_tag = False
            for p in p_list:
                paragragh_index += 1
                if '###' in p.get_text():
                    p_content = p.get_text()
                    if p_content[-1] == ' ':
                        p_content = p_content[:-1]
                    p_content = punct_pattern.sub(' ', p_content).replace(' ###', '###')
                    text = p_content.replace('###', '')
                    #print text
                    count = 0
                    pos = 0
                    pair_list = []
                    #print p_content
                    for i in range(alias_index, alias_index + p_content.count('###', 0, len(p_content))):
                        #print i
                        pair = {}
                        #print alias_list[i]
                        #print pos
                        relative_index = p_content.find(alias_list[i], pos)
                        #print p_content[relative_index:relative_index+len(alias_list[i]) - 3]
                        #print relative_index
                        begin_index = relative_index - 3 * count
                        if begin_index < 0:
                            pair_list = []
                            error_tag = True
                            total_negative_pair += 1
                            print 'negative begin index'
                            break
                        else:
                            #print begin_index
                            pos = relative_index + 1
                            end_index = begin_index + len(alias_list[i]) - 3
                            #print p_content[begin_index:end_index]
                            if text[begin_index:end_index] == alias_list[i][:-3]:
                                alias = alias_list[i][:-3]
                                entity = entity_list[i]
                                pair['begin_index'] = begin_index
                                pair['end_index'] = end_index
                                pair['alias'] = alias
                                pair['entity'] = entity
                                pair_list.append(pair)
                            else:
                                error_tag = True
                                print 'can not find'
                                can_not_find += 1
                                pair_list = []
                                break
                                # print content[begin_index:end_index]
                        count += 1
                    if error_tag:
                        break
                    else:
                        global total_entity_pair
                        if pair_list != []:
                            total_entity_pair += len(pair_list)
                            post_dict['text'] = text
                            post_dict['alias_entity'] = pair_list
                            post_dict['post_id'] = postid
                            post_dict['paragraph_id'] = paragragh_index
                            post_list.append(post_dict)
                        alias_index += p_content.count('###', 0, len(p_content))

#针对文件存在重复做了去重
def evaluate():
    print 'generate paragraph data'
    csv_reader = csv.reader(open('data/train so post/posts-question-answer.csv'))
    f = open('data/train so post/paragraph.json', 'w')
    index = 1
    id_dict = {}
    post_list = []
    for row in csv_reader:
        if index > 1:
            print index
            if row[0] not in id_dict:
                id_dict[row[0]] = 1
                if '<a href' in row[1]:
                    resolve(row[0], row[1], post_list)
        index += 1
    json.dump(post_list, f, indent=4)
    f.close()
    print 'correct: %d' % (len(post_list))
    print total_negative_pair
    print total_entity_pair
    print can_not_find

if __name__ == '__main__':
    #generateFromQuestionWithAnswerCSV()
    evaluate() #67839  #43863 post
    #print total_paragraph
    #print no_paragraph
    #print exist_paragraph