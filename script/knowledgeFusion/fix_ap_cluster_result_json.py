import json


def fix_ap_result(filename):
    with open(filename, 'r') as f:
        domain_entity_list = json.load(f)
    count = 1
    for each in domain_entity_list:
        each['id'] = count
        count = count + 1
    with open(filename, 'w') as f:
        json.dump(domain_entity_list, f)


if __name__ == "__main__":
    fix_ap_result('weight-0.5-depth-0.json')
