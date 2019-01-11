from py2neo import Graph
import csv
from os import path
import os
import json
import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# conn = mdb.connect(host='10.141.221.73', port=3306, user='root',
#                    passwd='root', db='codehub', charset='utf8')
# cursor = conn.cursor()

# cursor.execute("SELECT id, qualified_name FROM java_all_api_entity")
# entity_set = cursor.fetchall()

# cursor.execute("SELECT id, alias FROM java_api_alias")
# alias_set = cursor.fetchall()

# cursor.execute("SELECT * FROM has_alias")
# has_alias = cursor.fetchall()


def download():
    graph = Graph(
        "http://10.141.221.75:7474",
        username="root",
        password="123456"
    )

    nodes = graph.run("MATCH (n:entity) RETURN n.name, n.alias").data()
    return nodes


def preprocess(text):
    text = text.replace(".", "-1-")
    text = text.replace("_", "-2-")
    text = text.replace("(", "-3-")
    text = text.replace(")", "-4-")
    text = text.replace("<", "-5-")
    text = text.replace(">", "-6-")
    text = text.replace("[", "-7-")
    text = text.replace("]", "-8-")
    text = text.replace("()", "-9-")
    text = text.replace("[]", "-10-")
    return text


def process_data(nodes):
    data = []
    for node in nodes:
        entity = []
        if node["n.name"] is not None:
            if type(node["n.name"]) == str:
                entity.append(preprocess(node["n.name"]))
            elif type(node["n.name"]) == list:
                entity.extend([preprocess(name) for name in node["n.name"]])
        if node["n.alias"] is not None:
            if type(node["n.alias"]) == str:
                entity.append(preprocess(node["n.alias"]))
            elif type(node["n.alias"]) == list:
                entity.extend([preprocess(alias) for alias in node["n.alias"]])
        if len(entity) == 0:
            continue
        entity.insert(0, entity[0])
        for i in range(len(entity) - 1, -1, -1):
            if len(entity[i]) > 512:
                entity.pop(i)
        if len(entity) > 200:
            entity = entity[:200]
        if len(entity) > 0:
            data.append(entity)
    with open("entity/entity.csv", "wb") as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(data)


MAX_LINE = 30000
MAX_SIZE = 4 * 1024 * 1024


def split_file():
    file_size = os.path.getsize("entity/entity.csv")
    if file_size <= MAX_SIZE:
        return
    file_count = int(file_size / MAX_SIZE) + 1
    with open("entity/entity.csv", "r") as f:
        for i in range(file_count):
            text = f.read(MAX_SIZE)
            offset = 0
            while text[-1] != "\n":
                text = text[:-1]
                offset -= 1
            length = len(text)
            lines = text.split("\n")
            if len(lines) > MAX_LINE:
                text = "\n".join(lines[:MAX_LINE])
            print(len(text))
            offset -= (length - len(text))
            f.seek(offset, 1)
            with open("entity/entity-{}.csv".format(i), "w") as f_small:
                f_small.write(text)


# id2alias = {}
# for id, alias in alias_set:
#     id2alias[id] = alias

# entity2alias = {}
# for entity_id, alias_id in has_alias:
#     if entity2alias.get(entity_id) is None:
#         entity2alias[entity_id] = [alias_id]
#     else:
#         entity2alias[entity_id].append(alias_id)


# data = []
# for id, entity in entity_set:
#     row = [process_entity(entity), process_entity(entity)]
#     # print '"'+entity+'"'
#     if entity2alias.get(id) is not None:
#         for alias_id in entity2alias[id]:
#             alias = process_entity(id2alias[alias_id])
#             if alias not in row:
#                 row.append(alias)
#     data.append(row)

# count = int(len(data) / 10000) + 1
# for i in range(count - 1):
#     with open("entity/entity" + str(i) + ".csv", "wb") as f:
#         writer = csv.writer(f, dialect='excel')
#         writer.writerows(data[i * 5000: i * 5000 + 5000])
# with open("entity/entity" + str(count - 1) + ".csv", "wb") as f:
#     writer = csv.writer(f, dialect='excel')
#     writer.writerows(data[(count - 1) * 5000:])

statements = [
    "what is |{}",
    "could you tell me something about |{}",
    "please tell me something about |{}",
    "can you introduce |{}",
    "please give me some information about |{}",
    "please give me an introduction to |{}",
    "could you introduce |{}| to me",
    "could you give me some information about |{}",
    "please say something about |{}"
]

intent = {
    "name": "Query Single Entity Intent",
    "auto": True,
    "contexts": [],
    "responses": [
        {
            "resetContexts": False,
            "affectedContexts": [],
            "parameters": [],
            "messages": [
                {
                    "type": 0,
                    "speech": []
                }
            ],
            "defaultResponsePlatforms": {},
            "speech": []
        }
    ],
    "priority": 500000,
    "cortanaCommand": {
        "navigateOrService": "NAVIGATE",
        "target": ""
    },
    "webhookUsed": False,
    "webhookForSlotFilling": False,
    "fallbackIntent": False,
    "events": [],
    "userSays": [],
    "followUpIntents": [],
    "templates": []
}


MAX_USERSAY = 2000


def generate_intent():
    file_size = os.path.getsize("entity/entity.csv")
    file_count = int(file_size / MAX_SIZE) + 1
    entity_per_file = int(MAX_USERSAY / file_count / (len(statements) + 1))
    parameters = []
    speech = []
    userSays = []
    for i in range(file_count):
        param = {
            "required": False,
            "dataType": "@entity-" + str(i),
            "name": "entity-" + str(i),
            "value": "$entity-" + str(i),
            "isList": False
        }
        parameters.append(param)
        speech.append("$entity-" + str(i))
        with open("entity/entity-{}.csv".format(i), "r") as f:
            reader = csv.reader(f)
            entities = [row for row in reader]
        for _ in range(entity_per_file):
            entity = random.choice(entities)
            alias = random.choice(entity[1:])
            userSays.append({
                "data": [
                    {
                        "text": alias,
                        "alias": "entity-" + str(i),
                        "meta": "@entity-" + str(i),
                        "userDefined": False
                    }
                ],
                "isTemplate": False,
                "count": 0,
                "isAuto": False
            })
            for stmt in statements:
                texts = stmt.format(alias).split("|")
                # print(texts)
                usersay_data = []
                for text in texts:
                    usersay_data.append({"text": text})
                usersay_data[1]["alias"] = "entity-" + str(i)
                usersay_data[1]["meta"] = "@entity-" + str(i)
                usersay_data[1]["userDefined"] = False
                userSays.append({
                    "data": usersay_data,
                    "isTemplate": False,
                    "count": 0,
                    "isAuto": False
                })

    intent["responses"][0]["parameters"] = parameters
    intent["responses"][0]["messages"][0]["speech"] = speech
    intent["userSays"] = userSays
    with open("intent/querySingleEntityIntent.json", "w") as json_file:
        json.dump(intent, json_file)


if __name__ == "__main__":
    nodes = download()
    process_data(nodes)
    split_file()
    generate_intent()
