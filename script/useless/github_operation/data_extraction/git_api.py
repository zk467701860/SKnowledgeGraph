import requests
import time
import re
import json

def get_repository_topics_for_low_frequency(repository_url, mode='normal'):
    '''
    The maximum of frequency of access is 5000 per hour
    '''

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
              'Authorization': 'token ' + '44702440fac7f14adbd57e7cb08084c4dd036c32',
              'Accept': 'application/vnd.github.mercy-preview+json'}

    api_url_prefix = 'https://api.github.com/repos/'
    api_url = api_url_prefix + repository_url[19:]
    reconnect_count = 0

    while reconnect_count < 3:
        try:
            repository_json = requests.get(api_url, headers=header, timeout=30).json()
            if 'message' in repository_json:
                return []
            topics = repository_json['topics']
        except:
            reconnect_count += 1
            time.sleep(3)
        else:
            return topics

    raise Exception

def get_repository_topics_count(topic):

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
              'Authorization': 'token ' + '44702440fac7f14adbd57e7cb08084c4dd036c32',
              'Accept': 'application/vnd.github.mercy-preview+json'}
    api_url = 'https://api.github.com/search/repositories?q=topic:' + topic
    reconnect_count = 0

    while reconnect_count < 3:
        try:
            ret = requests.get(api_url, headers=header, timeout=30).json()

        except:
            reconnect_count += 1
            if reconnect_count > 3:
                return 0

        else:
            return int(ret['total_count'])

def get_repository_topics_list(topic, max=10):

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
              'Authorization': 'token ' + '44702440fac7f14adbd57e7cb08084c4dd036c32',
              'Accept': 'application/vnd.github.mercy-preview+json'}

    page = 1
    topics_list = []

    while True:

        api_url = 'https://api.github.com/search/repositories?q=topic:' + topic + '&page=' + str(page) + '&per_page=100'
        reconnect_count = 0

        try:
            ret = requests.get(api_url, headers=header, timeout=30).json()
            if ret['total_count'] == 0:
                return []
            for item in ret['items']:
                topics_list.append(item['html_url'])
                if len(topics_list) > max:
                    return topics_list

        except:
            reconnect_count += 1
            if reconnect_count > 3:
                return []

        else:
            page += 1
            if page > 10:
                break

            elif page > int(int(ret['total_count']) / 100) + 1:
                break

    return topics_list

def get_repository_related_topics(topic):
    pattern = 'location:related topics">([\s\S]{1,}?)</a>'

    url = 'https://github.com/topics/' + topic + '/related'
    reconnect_count = 0
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'}

    try:
        html = requests.get(url, headers=header, timeout=30).text
        match = re.findall(pattern, html)
        ret = [item.strip() for item in match]

    except:
            return []

    else:
        if len(match) == 0:
            return []

        return ret

def get_repository_info(repository_url):
    pattern = '<span class="num text-emphasized">([\s\S]{1,}?)</span>'
    description_pattern = '<div class="repository-meta-content col-11 mb-1">[\s\S]{1,}?</div>'

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'}

    try:
        html = requests.get(repository_url, headers=header, timeout=30).text
        match = re.findall(pattern, html)
        ret = [item.strip().replace(',', '') for item in match]
        match_description = re.findall(description_pattern, html)

        if len(match_description) == 0:
            description = ''
        else:
            description = match_description[0]

        commits = ret[0]
        branches = ret[1]
        releases = ret[2]
        contributors = ret[3]

    except:
        commits = branches = releases = contributors = -1
        description = None

    else:
        if len(match) == 0:
            commits = branches = releases = contributors = 0

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
              'Authorization': 'token ' + '44702440fac7f14adbd57e7cb08084c4dd036c32',
              'Accept': 'application/vnd.github.mercy-preview+json'}

    api_url = 'https://api.github.com/repos/' + repository_url[19:]

    reconnect_count = 0

    while True:

        try:
            repository_json = requests.get(api_url, headers=header, timeout=30).json()
            if 'message' in repository_json:
                topics = []
                stars = forks = -1
                license = 'null'
                break
        except:
            reconnect_count += 1
            time.sleep(3)
            if reconnect_count >= 3:
                topics = []
                stars = forks = -1
                license = 'null'
                break

        else:
            topics = repository_json['topics']
            forks = repository_json['forks']
            stars = repository_json['stargazers_count']
            if repository_json['license'] == None:
                license = 'null'
            else:
                license = repository_json['license']['name']
                if license == None:
                    license = 'null'
            break
    url = repository_url
    keys = ('description', 'url', 'star', 'fork', 'commit', 'branch', 'release', 'contributor', 'license', 'topics')
    values = (description, url, stars, forks, commits, branches, releases, contributors, license, topics)
    dic = {}
    for index in range(len(keys)):
        dic[keys[index]] = values[index]

    return json.dumps(dic)

def get_repository_description(repository_url):

    pattern = 'data-octo-dimensions="topic:([\s\S]{1,}?)">'
    description_pattern = '<div class="repository-meta-content col-11 mb-1">[\s\S]{1,}?</div>'
    reconnect_count = 0
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'}
    while True:
        try:
            html = requests.get(repository_url, headers=header, timeout=30).text
        except:
            reconnect_count += 1
            if reconnect_count > 3:
                topics = []
                description = ''
                break
        else:
            match = re.findall(pattern, html)
            match_description = re.findall(description_pattern, html)
            if len(match) == 0:
                topics = []
            else:
                topics = match

            if len(match_description) == 0:
                description = ''
            else:
                description = match_description[0]
            break

    dic = {}
    dic['description'] = description
    dic['topic'] = topics
    dic['url'] = repository_url

    return json.dumps(dic)
