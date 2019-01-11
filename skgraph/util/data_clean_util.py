import textdistance


def get_name_by_github_url(github_url):
    url_fragment_list = github_url.split("/")
    #print len(url_fragment_list), " ", url_fragment_list
    if len(url_fragment_list) < 5:
        return ""
    else:
        return url_fragment_list[4]


def construct_key_count_map(node_list):
    node_map = {}
    for node in node_list:
        if "name" in dict(node):
            name = node["name"]
            if name in node_map:
                node_map[name].append(node)
            else:
                node_map.setdefault(name, [node])
    return node_map


def extract_url_main_part(url):
    result = ""
    if url.find("://") != -1:
        temp = url[url.find("://")+3:]
        if temp.find("/") != -1:
            result = temp[:temp.find("/")]
        else:
            result = temp
    else:
        if url.find("/") != -1:
            if url.find("/") == 0:
                result = url[1:]
            else:
                result = url[:url.find("/")]
        else:
            result = url
    return result


def url_similarity(url1, url2):
    result = 0
    if "://github.com" not in url1 and "://github.com" not in url2:
        url1_main_part = extract_url_main_part(url1)
        url2_main_part = extract_url_main_part(url2)
        result = textdistance.jaccard(url1_main_part, url2_main_part)
    elif "://github.com" in url1 and "://github.com" not in url2:
        url1_main_part = get_name_by_github_url(url1)
        #url2_main_part = extract_url_main_part(url2)
        # print "url1: ", url1, " url1_main: ", url1_main_part, " url2: ", url2, " url2_main: ", url2
        lcsstr = textdistance.lcsstr(url1_main_part, url2)
        min_len = min(len(url1_main_part), len(url2))
        if min_len == 0:
            min_len = 1
        result = len(lcsstr) * 1.0 / min_len
    elif "://github.com" not in url1 and "://github.com" in url2:
        #url1_main_part = extract_url_main_part(url1)
        url2_main_part = get_name_by_github_url(url2)
        # print "url1: ", url1, " url1_main: ", url1, " url2: ", url2, " url2_main: ", url2_main_part
        lcsstr = textdistance.lcsstr(url1, url2_main_part)
        min_len = min(len(url1), len(url2_main_part))
        if min_len == 0:
            min_len = 1
        result = len(lcsstr) * 1.0 / min_len
    else:
        url1_main_part = get_name_by_github_url(url1)
        url2_main_part = get_name_by_github_url(url2)
        result = textdistance.jaccard(url1_main_part, url2_main_part)
    return result


def description_similarity(description1, description2):
    return textdistance.jaccard(description1, description2)


def property_in_dict_list(property, dict_list):
    for each in dict_list:
        if property in each:
            return True
    return False


def rename_property(node_list):
    property_set = construct_property_set(node_list)
    i = 0
    for node in node_list:
        node_properties = dict(node).keys()
        for each in node_properties:
            if each in property_set and each != "name":
                new_property = each + "#" + str(i)
                node[new_property] = node.pop(each)
        i += 1
    return node_list


def construct_property_set(node_list):
    result_set = set()
    property_list = []
    for node in node_list:
        node_properties = set(dict(node).keys())
        property_list.append(node_properties)

    for i in range(0, len(property_list) - 1):
        for j in range(i + 1, len(property_list)):
            result_set = result_set | (property_list[i] & property_list[j])
    return result_set