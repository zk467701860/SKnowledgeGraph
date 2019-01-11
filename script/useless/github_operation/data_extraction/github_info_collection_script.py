import json

from script.github_operation.data_extraction.git_api import get_repository_info

with open("github_data.json", "r") as f:
    github_url_list = json.load(f)

with open("github_info.data", "a+") as f:
    for each in github_url_list:
        id = each.get("id")
        github_url = each.get("github_url")
        if github_url and github_url != "" and github_url.find("/releases") == -1 and github_url.find("/issues") == -1  and github_url.find("/milestones") == -1 and github_url.find("/labels") == -1 and id > 14596:
            github_info_str = get_repository_info(github_url)
            github_info_dict = json.loads(github_info_str)
            each.update(github_info_dict)
            print "NO." + str(id) + " has finished collection"
            f.write(json.dumps(each) + '\n')