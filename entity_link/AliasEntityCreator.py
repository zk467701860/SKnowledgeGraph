# encoding: utf-8
from corpus import ProcessorAliasCount, AliasStatisticsUtil
from aggregateCount import CountSystem
import os
import MySQLdb
import sys
import json
from NormalizeUtil import transform_url_to_qualifier
from NormalizeUtil import isLegalAlias

reload(sys)
sys.setdefaultencoding('utf8')

def mergeInputData():
    rootdir = 'data'
    #file_list = os.listdir(rootdir)
    map_dict = {'android_html.json': 'android_alias_link.json', 'androidGuide_html.json': 'androidGuide_alias_link.json', 'JDK_html.json': 'JDK_alias_link.json', 'JDKGuide_html.json': 'JDKGuide_alias_link.json'}
    '''
    for i in range(0, len(file_list)):
        if '_html.json' in file_list[i]:
            alias_file = file_list[i].replace('html', 'alias_link')
            if alias_file in file_list:
                map_dict[file_list[i]] = alias_file
    '''
    #output_html_path = os.path.join(rootdir, 'html.json')
    output_link_path = os.path.join(rootdir, 'alias_link.json')
    #合并Java和Android的四个数据源html内容，append即可
    '''
    html_content = []
    print 'initial html count:  %d' % (len(html_content))
    for html_json_file in map_dict:
        html_json_path = os.path.join(rootdir, html_json_file)
        print 'insert html :  %s ' % (html_json_path)
        with open(html_json_path, 'r') as load_f:
            load_dict = json.load(load_f)
            print len(load_dict)
            html_content.extend(load_dict)
            print 'total:  %d' % (len(html_content))
    print 'total store html count:  %d' % (len(html_content))
    with open(output_html_path, 'w') as write_f:
        json.dump(html_content, write_f)
    print 'html generate done'
    '''
    # 合并四个数据源alias link内容，需要合并相同项，同时这里就筛选出了仅为API的别名和实体对
    html_content = []
    alias_link_dict = {}
    for html_json_file in map_dict:
        alise_link_json_path = os.path.join(rootdir, map_dict[html_json_file])
        print 'insert alias :  %s ' % (alise_link_json_path)
        with open(alise_link_json_path, 'r') as load_f:
            load_dict = json.load(load_f)
            print 'total pair:  %d' % (len(load_dict))
            index = 0
            for pair in load_dict:
                entity = transform_url_to_qualifier(pair['link'])
                if entity != '':
                    alias = isLegalAlias(pair['alias'])
                    if alias != '':
                        index += 1
                        key = alias + '###' + entity
                        alias_link_dict[key] = alias_link_dict.get(key, 0) + pair['count']
                        if index % 10000 == 0:
                            print index
                            print 'current dict total:  %d' % (len(alias_link_dict))
            print 'correct pair:  %d' % (index)
            print 'dict total:  %d' % (len(alias_link_dict))

    # 合并so alias link内容，需要合并相同项，同时这里就筛选出了仅为API的别名和实体对
    so_json_path = os.path.join(rootdir, 'statistic_result_all.json')
    print 'insert so alias'
    with open(so_json_path, 'r') as load_f:
        load_dict = json.load(load_f)
        print 'total pair:  %d' % (len(load_dict))
        index = 0
        for pair in load_dict:
            entity = transform_url_to_qualifier(pair['link'])
            if entity != '':
                alias = isLegalAlias(pair['alias'])
                if alias != '':
                    index += 1
                    key = alias + '###' + entity
                    alias_link_dict[key] = alias_link_dict.get(key, 0) + pair['times']
        print 'correct pair:  %d' % (index)
        print 'dict total:  %d' % (len(alias_link_dict))
    for key in alias_link_dict:
        alias_entity = key.split('###')
        alias = alias_entity[0]
        entity_id = alias_entity[1]
        new_dict = {}
        new_dict['count'] = alias_link_dict[key]
        new_dict['alias'] = alias
        new_dict['link'] = entity_id
        html_content.append(new_dict)
    with open(output_link_path, 'w') as write_f:
        json.dump(html_content, write_f)
    #return output_html_path, output_link_path

def copySOHtml2File():
    print 'begin read so html from so mysql'
    beginId = 0
    stepSize = 50000
    file_index = 1
    file_path = 'data/SO_html_' + str(file_index) + '.txt'
    try:
        conn = MySQLdb.connect(host='10.131.252.160', user='root', passwd='root', port=3306, db='stackoverflow',
                               charset='utf8')
        cur = conn.cursor()
    except MySQLdb.Error, e:
        print "Mysql connection Error %d: %s" % (e.args[0], e.args[1])
    try:
        sql = 'select body from clean_posts_android_java where id > %d limit %d' % (beginId, stepSize)
        cur.execute(sql)
        data = cur.fetchall()
        f = open(file_path, 'w')
        while data != ():
            for content in data:
                f.writelines("%s\n" % (content[0]))
            beginId += stepSize
            if beginId % 400000 == 0:
                f.close()
                file_index += 1
                file_path = 'data/SO_html_' + str(file_index) + '.txt'
                f = open(file_path, 'w')
                print 'finish %d' % (beginId)
            sql = 'select body from clean_posts_android_java where id > %d limit %d' % (beginId, stepSize)
            cur.execute(sql)
            data = cur.fetchall()
        print 'finish count occur from so mysql'
    except Exception as e:
        conn.rollback()
        print('MySQL: %s   error:%s' % (sql, e))
    cur.close()
    conn.close()

#将不同数据源的html和alias-link的json文件进行合并，筛选出API相关的条目，并生成计算先验概率需要的tsv文件
if __name__=="__main__":
    '''
    mergeInputData()
    html_path, alias_link_path = mergeInputData()
    '''
    #copySOHtml2File()

    mergeInputData()
    html_path = 'data/html.json'
    alias_link_path = 'data/alias_link.json'
    processor = ProcessorAliasCount()
    new_vocabulary_path = 'data/normalize_alias_link.json'
    aliasStatisticsUtil = AliasStatisticsUtil(alias_ngram=False)
    processor.process_alias_2_entity_map(alias_link_path, new_vocabulary_path)
    aliasStatisticsUtil.init_vocabulary_from_json(new_vocabulary_path)
    aliasStatisticsUtil.count_occur_from_json(html_path)

    rootDir = 'data/so_html'
    file_list = os.listdir(rootDir)
    so_html_list = []
    for i in range(0, len(file_list)):
        if 'SO_html_' in file_list[i]:
            so_html_list.append(os.path.join(rootDir, file_list[i]))
    for so_html_file in so_html_list:
        aliasStatisticsUtil.count_occur_from_file(so_html_file)
    #aliasStatisticsUtil.count_occur_from_json(html_path)

    aliasStatisticsUtil.add_mysql_alias_to_system()
    aliasStatisticsUtil.output_intermediate_data()
    final_tsv_path = "data/alias-entity-counts.tsv"
    aliasStatisticsUtil.write_to_tsv(final_tsv_path)
    aggregate_system = CountSystem()
    aggregate_system.new_count(final_tsv_path)


    #partial run
    '''
    new_vocabulary_path = 'data/without so/normalize_alias_link.json'
    aliasStatisticsUtil = AliasStatisticsUtil(alias_ngram=False)
    aliasStatisticsUtil.init_vocabulary_from_json(new_vocabulary_path)
    aliasStatisticsUtil.partial_run(new_vocabulary_path)
    final_tsv_path = "data/without so/alias-entity-counts.tsv"
    aliasStatisticsUtil.write_to_tsv(final_tsv_path)
    aggregate_system = CountSystem()
    aggregate_system.new_count(final_tsv_path)
    '''


