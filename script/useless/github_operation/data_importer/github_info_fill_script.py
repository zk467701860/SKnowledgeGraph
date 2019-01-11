import codecs
import json
import os

from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.node_collection import NodeCollection
from skgraph.util.code_text_process import clean_html_text, clean_html_text_with_format


def get_github_dict_by_id(id):
    for each in github_info_list:
        each_id = each["id"]
        if id == each_id:
            return each
    return dict()


node_collection = NodeCollection(GraphClient(server_number=0))
node_list = node_collection.get_all_nodes(1000, ['awesome item'])
print len(node_list)

filename = "github_info.data"
filepath = os.path.abspath(os.path.dirname(os.getcwd())) + "/" + filename

with open(filepath, "r") as f:
    lines = f.readlines()

github_info_list = []
for line in lines:
    github_info_dict = json.loads(line)
    github_info_list.append(github_info_dict)

for each in github_info_list:
    #print each["id"]
    if "description" in each:
        each["description"] = clean_html_text(each["description"])
    if "contributor" in each:
        if type(each["contributor"]) != int:
            each["contributor"] = clean_html_text(each["contributor"])
        elif each["contributor"] == -1:
            each["contributor"] = 0
    if "release" in each and each["release"] == -1:
        each["release"] = 0
    if "branch" in each and each["branch"] == -1:
        each["branch"] = 0
    if "commit" in each and each["commit"] == -1:
        each["commit"] = 0


temp_extended_list = []
j = 0
remain_list = []
for i in range(0, len(github_info_list)):
    if "fork" in github_info_list[i] and "star" in github_info_list[i]:
        fork = github_info_list[i]["fork"]
        star = github_info_list[i]["star"]
        if fork != -1 and star != -1:
            old_url = dict(node_list[j])["url"]
            new_url = github_info_list[i]["github_url"]
            # print old_url, " ", new_url
            while old_url != new_url:
                if j >= len(node_list) - 1:
                    j = 0
                    remain_list.append(github_info_list[i]["id"])
                    break
                j += 1
                old_url = dict(node_list[j])["url"]
            if j != 0 or i == 0:
                temp = dict(node_list[j])
                for key in github_info_list[i].keys():
                    if key == "id":
                        continue
                    else:
                        temp_key = "github:" + key
                        temp.setdefault(temp_key, github_info_list[i][key])
                temp_extended_list.append(temp)

for each in temp_extended_list:
    print each

len1 = len(temp_extended_list)

for each in remain_list:
    each_dict = get_github_dict_by_id(each)
    #print each_dict
    if "fork" in each_dict and "star" in each_dict:
        fork = each_dict["fork"]
        star = each_dict["star"]
        if fork != -1 and star != -1:
            new_url = each_dict["github_url"]
            for node in node_list:
                old_url = dict(node)["url"]
                if new_url == old_url:
                    temp = dict(node)
                    for key in each_dict.keys():
                        if key == "id":
                            continue
                        else:
                            temp_key = "github:" + key
                            temp.setdefault(temp_key, each_dict[key])
                        temp_extended_list.append(temp)
                    break

len2 = len(temp_extended_list)
print len1, " ", len2
with codecs.open('temp_data.json', 'w', encoding='utf8') as f:
    json.dump(temp_extended_list, f, ensure_ascii=False, encoding='utf8')
