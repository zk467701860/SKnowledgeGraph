import csv
import random
import json
import os

statements = [
    "what is the |{}| of |{}",
    "{}| of |{}",
    "tell me |{}| of |{}"
]


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


def process_data():
    with open("property/original_property.csv", "r") as f:
        reader = csv.reader(f)
        prop_list = [[preprocess(row[0])] for row in reader]

    with open("property/property.csv", "wb") as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(prop_list)


intent = {
    "name": "Query Property Of Entity Intent",
    "auto": True,
    "contexts": [],
    "responses": [
        {
            "resetContexts": False,
            "affectedContexts": [],
            "parameters": [
                {
                    "required": False,
                    "dataType": "@property",
                    "name": "property",
                    "value": "$property",
                    "isList": False
                }
            ],
            "messages": [
                {
                    "type": 0,
                    "speech": [
                    ]
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
MAX_SIZE = 4 * 1024 * 1024
SELECTED_PROPERTY = 30


def generate_intent():
    userSays = []
    with open("property/property.csv", "r") as f:
        reader = csv.reader(f)
        properties = [row[0] for row in reader]
    entity_file_size = os.path.getsize("entity/entity.csv")
    entity_file_count = int(entity_file_size / MAX_SIZE) + 1
    entity_per_file = int(MAX_USERSAY / SELECTED_PROPERTY / entity_file_count / len(statements))
    for i in range(entity_file_count):
        param = {
            "required": False,
            "dataType": "@entity-" + str(i),
            "name": "entity-" + str(i),
            "value": "$entity-" + str(i),
            "isList": False
        }
        intent["responses"][0]["parameters"].append(param)
        intent["responses"][0]["messages"][0]["speech"].append("$entity-" + str(i) + ",$property")
        with open("entity/entity-{}.csv".format(i), "r") as f:
            reader = csv.reader(f)
            entities = [row for row in reader]
        for _ in range(entity_per_file):
            entity = random.choice(entities)
            alias = random.choice(entity[1:])
            for _ in range(SELECTED_PROPERTY):
                property = random.choice(properties)
                texts = statements[0].format(property, alias).split("|")
        # print(texts)
                usersay_data = []
                for text in texts:
                    usersay_data.append({"text": text})
                usersay_data[1]["alias"] = "property"
                usersay_data[1]["meta"] = "@property"
                usersay_data[1]["userDefined"] = False
                usersay_data[3]["alias"] = "entity-" + str(i)
                usersay_data[3]["meta"] = "@entity-" + str(i)
                usersay_data[3]["userDefined"] = False
                userSays.append({
                    "data": usersay_data,
                    "isTemplate": False,
                    "count": 0,
                    "isAuto": False
                })

                texts = statements[1].format(property, entity).split("|")
                # print(texts)
                usersay_data = []
                for text in texts:
                    usersay_data.append({"text": text})
                usersay_data[0]["alias"] = "property"
                usersay_data[0]["meta"] = "@property"
                usersay_data[0]["userDefined"] = False
                usersay_data[2]["alias"] = "entity-" + str(i)
                usersay_data[2]["meta"] = "@entity-" + str(i)
                usersay_data[2]["userDefined"] = False
                userSays.append({
                    "data": usersay_data,
                    "isTemplate": False,
                    "count": 0,
                    "isAuto": False
                })

                texts = statements[2].format(property, alias).split("|")
        # print(texts)
                usersay_data = []
                for text in texts:
                    usersay_data.append({"text": text})
                usersay_data[1]["alias"] = "property"
                usersay_data[1]["meta"] = "@property"
                usersay_data[1]["userDefined"] = False
                usersay_data[3]["alias"] = "entity-" + str(i)
                usersay_data[3]["meta"] = "@entity-" + str(i)
                usersay_data[3]["userDefined"] = False
                userSays.append({
                    "data": usersay_data,
                    "isTemplate": False,
                    "count": 0,
                    "isAuto": False
                })

    intent["userSays"] = userSays
    with open("intent/queryPropertyOfEntityIntent.json", "w") as json_file:
        json.dump(intent, json_file)
# print(intent)


if __name__ == "__main__":
    process_data()
    generate_intent()
