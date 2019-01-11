# encoding: utf-8
import csv
from bs4 import BeautifulSoup, Comment
from NormalizeUtil import transform_url_to_qualifier
from NormalizeUtil import isLegalAlias
from filter import TextPreprocessor
import re
import json

total_entity_pair = 0
total_negative_pair = 0
can_not_find = 0

def resolve(post_id, content, post_list):
    processor = TextPreprocessor()
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
    content = soup.get_text(separator=" ")
    content = punct_pattern.sub(' ', content)
    if content[-1] == ' ':
        content = content[:-1]
    #print content
    post_dict['id'] = post_id
    post_dict['text'] = content
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
    new_content = soup.get_text(separator=" ")
    if new_content[-1] == ' ':
        new_content = new_content[:-1]
    #print '!!!!!!!!!!!!!!'
    #print new_content
    new_content = punct_pattern.sub(' ', new_content).replace(' ###', '###')
    #print new_content
    pos = 0
    count = 0
    pair_list = []
    #print '!!!!!!!!!!!!!!'
    # new_content
    global can_not_find
    global total_negative_pair
    for i in range(0, len(alias_list)):
        pair = {}
        #print alias_list[i]
        #print pos
        relative_index = new_content.find(alias_list[i], pos)
        #print new_content[relative_index:relative_index+len(alias_list[i]) - 3]
        #print relative_index
        begin_index = relative_index - 3 * count
        if begin_index < 0:
            pair_list = []
            total_negative_pair += 1
            break
        else:
            #print begin_index
            pos = relative_index + 1
            end_index = begin_index + len(alias_list[i]) - 3
            if content[begin_index:end_index] == alias_list[i][:-3]:
                alias = alias_list[i][:-3]
                entity = entity_list[i]
                pair['begin_index'] = begin_index
                pair['end_index'] = end_index
                pair['alias'] = alias
                pair['entity'] = entity
                pair_list.append(pair)
            else:
                can_not_find += 1
            #print content[begin_index:end_index]
        count += 1
    global total_entity_pair
    if pair_list != []:
        total_entity_pair += len(pair_list)
        post_dict['alias_entity'] = pair_list
        post_list.append(post_dict)

def generateFromQuestionWithAnswerCSV():
    print 'generateFromQuestionWithAnswerCSV'
    csv_reader = csv.reader(open('data/train so post/data-score0.csv'))
    index = 1
    f = open('data/train so post/question-answer.json', 'w')
    post_list = []
    for row in csv_reader:
        if index > 1:
            print index
            if '<a href' in row[2]:
                resolve(row[2], post_list)
            if '<a href' in row[3]:
                resolve(row[3], post_list)
        index += 1
    json.dump(post_list, f, indent=4)
    f.close()

#针对文件存在重复做了去重
def generateFromSinglePostCSV():
    print 'generateFromSinglePostCSV'
    csv_reader = csv.reader(open('data/train so post/posts-question-answer.csv'))
    index = 1
    f = open('data/train so post/post.json', 'w')
    post_list = []
    id_dict = {}
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

if __name__ == '__main__':
    #generateFromQuestionWithAnswerCSV()
    generateFromSinglePostCSV() #67839  #43863 post
    #print total_entity_pair
    #print total_negative_pair
    #print can_not_find
    #print error_list
    #post_list = []
    #post.json 1443
    #test_data = "drawing part of a bitmap on an Android canvas <p>How can you blit a non-rectangular (e.g. oval) part of a bitmap into a canvas on Android?</p>&#xA;&#xA;<p>Consider how you'd blit a rectangular part of a bitmap:&#xA;<a href=""http://developer.android.com/reference/android/graphics/Canvas.html#drawBitmap%28android.graphics.Bitmap,%20android.graphics.Rect,%20android.graphics.Rect,%20android.graphics.Paint%29"" rel=""nofollow""><code>canvas.DrawBitmap(src,src_rect,dest_rect,paint)</code></a>.  Sadly there is no corresponding methods for non-rectangular regions.</p>&#xA;&#xA;<p>Four approaches present themselves (maybe you know a fifth?):</p>&#xA;&#xA;<ol>&#xA;<li><p>copy the rectangular bounds you want to blit into an intermediate bitmap, and go setting the pixels you don't want to blit to be transparent, then draw that bitmap</p></li>&#xA;<li><p>make a mask bitmap - there are ways to blit with a separate mask?</p></li>&#xA;<li><p>use a <a href=""http://developer.android.com/reference/android/graphics/BitmapShader.html"" rel=""nofollow""><code>BitmapShader</code></a> with <a href=""http://developer.android.com/reference/android/graphics/Canvas.html#drawArc%28android.graphics.RectF,%20float,%20float,%20boolean,%20android.graphics.Paint%29"" rel=""nofollow""><code>drawArc()/drawCircle()</code></a>; however, I can't work out how to get the <strong><em>matrix</em></strong> to be properly aligned; how would you initialize the matrix for this operation?</p></li>&#xA;<li><p>use a very very complicated clipping region</p></li>&#xA;</ol>&#xA;&#xA;<p>Of these, <strong><em>option 3</em></strong> is the one that I would most like to work; however, I cannot work out how to do so; can you?</p>&#xA;"
    #resolve(100, test_data, post_list)
    #print post_list

