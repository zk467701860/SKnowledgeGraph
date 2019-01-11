# -*- coding: utf-8 -*-
# import urllib2
import requests
from requests.exceptions import ReadTimeout,HTTPError,RequestException
import re
from bs4 import BeautifulSoup, Comment
import json
import sys
reload(sys) 
sys.setdefaultencoding('utf-8') 


url_prefix = 'https://developer.android.com/reference/'
htmls = []
alias_url = []
alias_url_dict = {}
inner_alias_url = []
outer_alias_url = []
inner_alias_url_dict = {}
outer_alias_url_dict = {}

sucess_list = []
failed_list = []
counter = 0

def get_url():
    urls = []
    # req = urllib2.Request(url_prefix+'overview-frame.html')
    # res = urllib2.urlopen(req)
    res = requests.get(url_prefix+'packages', timeout=10)

    # data = res.text
    soup = BeautifulSoup(res.text, 'lxml')
    # print(soup.find_all("a", target="packageFrame"))
    
    for a in soup.select("tr .jd-linkcol a"):
        alias = a.string
        url = a['href']
        if alias_url_dict.get((alias, url)) is None:
            alias_url_dict[(alias, url)] = 1
        else:
            alias_url_dict[(alias, url)] += 1
        urls.append(url)

    res.close()

    # req = urllib2.Request(url_prefix+'allclasses-frame.html')
    # res = urllib2.urlopen(req)
    # data = res.read()
    res = requests.get(url_prefix+'classes')
    soup = BeautifulSoup(res.text, 'lxml')
    # print(soup.find_all("a", target="packageFrame"))
    for a in soup.select("table tr .jd-linkcol a"):
        alias = a.string
        url = a['href']
        if alias_url_dict.get((alias, url)) is None:
            alias_url_dict[(alias, url)] = 1
        else:
            alias_url_dict[(alias, url)] += 1
        urls.append(url)
    res.close()
    with open('raw_data_android/urls.json', 'w') as f:
        json.dump(urls, f)
    return urls

def get_prefix(url):
    for i in range(len(url)-1, -1, -1):
        if url[i] == "/":
            return url[:i+1]
    return url

pattern1 = re.compile(r'<.*?>')
pattern2 = re.compile(r' {2,}')
pattern3 = re.compile(r'(http://|https://)?developer\.android\.com.*')
pattern4 = re.compile(r'.*\.(com|org|cn|edu).*')

def clean_html(text):
    '''
    clean text format for text extract from html
    :param text:
    :return:
    '''
    s = pattern1.sub("", text.replace('\n', ' ').replace(u'\u00a0', " "))
    return pattern2.sub(" ", s)

def get_html(urls):
    global counter
    global alias_url
    global inner_alias_url
    global outer_alias_url
    for url in urls:
        print(url)
        # req = urllib2.Request(url)
        # res = urllib2.urlopen(req)
        # data = res.read()
        try:
            res = requests.get(url, timeout=10)
            print(res.status_code)
        except ReadTimeout:
            failed_list.append(url)
            print('timeout')
            continue
        except HTTPError:
            failed_list.append(url)
            print('httperror')
            continue
        except RequestException:
            failed_list.append(url)
            print('reqerror')
            continue
        if res.status_code != 200:
            failed_list.append(url)
            continue
        soup = BeautifulSoup(res.text, 'lxml')
        res.close()
        # text = str(soup.select('.header')[0])
        # header = str(soup.select('.header')[0]).replace(u'\u00a0', " ")
        html = soup.find(itemtype="http://developers.google.com/ReferenceObject").get_text()
        soup = BeautifulSoup(html, 'lxml')
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        html = str(soup)
        for a in soup.select('a'):
            alias_ = a.string
            if alias_ is None or alias_ == "":
                continue
            alias_ = alias_.replace("\n", "").strip()
            if alias_ == "":
                continue
            if a.get('href') is None:
                continue
            if len(a['href']) == 0:
                continue
            url_ = ""
            if a['href'][0] == '#':
                url_ = url + a['href']
                if inner_alias_url_dict.get((alias_, url_)) is None:
                    inner_alias_url_dict[(alias_, url_)] = 1
                else:
                    inner_alias_url_dict[(alias_, url_)] += 1
            elif a['href'][0] != ".":
                url_ = a['href']
                if pattern3.match(a['href']) is not None:
                    if inner_alias_url_dict.get((alias_, url_)) is None:
                        inner_alias_url_dict[(alias_, url_)] = 1
                    else:
                        inner_alias_url_dict[(alias_, url_)] += 1
                elif pattern4.match(a['href']) is not None:
                    url_ = get_prefix(url) + a['href']
                    if inner_alias_url_dict.get((alias_, url_)) is None:
                        inner_alias_url_dict[(alias_, url_)] = 1
                    else:
                        inner_alias_url_dict[(alias_, url_)] += 1
                else:
                    if outer_alias_url_dict.get((alias_, url_)) is None:
                        outer_alias_url_dict[(alias_, url_)] = 1
                    else:
                        outer_alias_url_dict[(alias_, url_)] += 1
            else:
                url_ = get_prefix(url) + a['href']
                if inner_alias_url_dict.get((alias_, url_)) is None:
                    inner_alias_url_dict[(alias_, url_)] = 1
                else:
                    inner_alias_url_dict[(alias_, url_)] += 1
            if alias_url_dict.get((alias_, url_)) is None:
                alias_url_dict[(alias_, url_)] = 1
            else:
                alias_url_dict[(alias_, url_)] += 1
        clean_text = clean_html(html)
        # print(clean_format(text))
        htmls.append({
            'url': url,
            'html': html,
            'clean_text': clean_text
        })
        sucess_list.append(url)
        counter += 1
        if counter % 100 == 0:
            for (alias, url) in alias_url_dict.keys():
                alias_url.append({
                    'alias': alias,
                    'link': url,
                    'count': alias_url_dict[(alias, url)]
                })
            for (alias, url) in inner_alias_url_dict.keys():
                inner_alias_url.append({
                    'alias': alias,
                    'link': url,
                    'count': inner_alias_url_dict[(alias, url)]
                })
            for (alias, url) in outer_alias_url_dict.keys():
                outer_alias_url.append({
                    'alias': alias,
                    'link': url,
                    'count': outer_alias_url_dict[(alias, url)]
                })
            with open("raw_data_android/html.json", "w") as f:
                json.dump(htmls, f)
            with open("raw_data_android/alias_link.json", "w") as f:
                json.dump(alias_url, f)
            with open("raw_data_android/inner_alias_link.json", "w") as f:
                json.dump(inner_alias_url, f)
            with open("raw_data_android/outer_alias_link.json", "w") as f:
                json.dump(outer_alias_url, f)
            with open("raw_data_android/sucess_list.json", "w") as f:
                json.dump(sucess_list, f)  
            with open("raw_data_android/failed_list.json", "w") as f:
                json.dump(failed_list, f)  
            alias_url = []
            inner_alias_url = []
            outer_alias_url = []
    for (alias, url) in alias_url_dict.keys():
        alias_url.append({
            'alias': alias,
            'link': url,
            'count': alias_url_dict[(alias, url)]
        })
    for (alias, url) in inner_alias_url_dict.keys():
        inner_alias_url.append({
            'alias': alias,
            'link': url,
            'count': inner_alias_url_dict[(alias, url)]
        })
    for (alias, url) in outer_alias_url_dict.keys():
        outer_alias_url.append({
            'alias': alias,
            'link': url,
             'count': outer_alias_url_dict[(alias, url)]
        })       

def parse(urls):
    global failed_list
    try:
        while len(urls) > 0:
            print('\n--------------------------\n')
            get_html(urls)
            urls = failed_list
            failed_list = []
    except MemoryError:
        pass
    with open("raw_data_android/html.json", "w") as f:
        json.dump(htmls, f)
    with open("raw_data_android/alias_link.json", "w") as f:
        json.dump(alias_url, f)
    with open("raw_data_android/inner_alias_link.json", "w") as f:
        json.dump(inner_alias_url, f)
    with open("raw_data_android/outer_alias_link.json", "w") as f:
        json.dump(outer_alias_url, f)
    with open("raw_data_android/sucess_list.json", "w") as f:
        json.dump(sucess_list, f)  
    with open("raw_data_android/failed_list.json", "w") as f:
        json.dump(failed_list, f) 


if __name__ == "__main__":
    urls = get_url()
    parse(urls)

    # print(pattern3.match("fds/a.html"))

    
# import urllib2

# req = urllib2.Request('http://www.baidu.com')
# res = urllib2.urlopen(req)
# print res.code
# print res.read()
# res.close()

