import csv
import random
import json
import os

statements = [
    "what is related to |{}",
    "which entity is related to |{}",
    "tell me the entity related to |{}",
    "tell me which entity is related to |{}",
    "related to |{}"
]


# with open("relation/original_relation.csv", "r") as csv_file:
#     reader = csv.reader(csv_file)
#     prop_list = [[process_prop(raw[0])] for raw in reader]

# with open("relation/relation.csv", "wb") as csv_file:
#     writer = csv.writer(csv_file, dialect='excel')
#     writer.writerows(prop_list)


intent = {
    "name": "Query Related Entity Intent",
    "auto": True,
    "contexts": [],
    "responses": [
        {
            "resetContexts": False,
            "affectedContexts": [],
            "parameters": [
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

def generate_intent():
    file_size = os.path.getsize("entity/entity.csv")
    file_count = int(file_size / MAX_SIZE) + 1
    entity_per_file = int(MAX_USERSAY / file_count / len(statements))
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
    with open("intent/queryRelatedEntityIntent.json", "w") as json_file:
        json.dump(intent, json_file)

if __name__ == "__main__":
    generate_intent()

# userSays = []

# for i in range(entity_file_count):
#     param = {
#         "required": False,
#         "dataType": "@entity" + str(i),
#         "name": "entity" + str(i),
#         "value": "$entity" + str(i),
#         "isList": False
#     }
#     intent["responses"][0]["parameters"].append(param)
#     intent["responses"][0]["messages"][0]["speech"].append("$entity" + str(i) + ",$relation")
#     with open("entity/entity" + str(i) + ".csv", "r") as csv_file:
#         reader = csv.reader(csv_file)
#         entity_list = [raw[0] for raw in reader]
#         for _ in range(entity_count_per_file):
#             entity = random.choice(entity_list)
#             for _ in range(selected_prop_count):
#                 property = random.choice(prop_list)[0]
#                 texts = statements[0].format(property, entity).split("|")
#     # print(texts)
#                 usersay_data = []
#                 for text in texts:
#                     usersay_data.append({"text": text})
#                 usersay_data[1]["alias"] = "relation"
#                 usersay_data[1]["meta"] = "@relation"
#                 usersay_data[1]["userDefined"] = False
#                 usersay_data[3]["alias"] = "entity" + str(i)
#                 usersay_data[3]["meta"] = "@entity" + str(i)
#                 usersay_data[3]["userDefined"] = False
#                 userSays.append({
#                     "data": usersay_data,
#                     "isTemplate": False,
#                     "count": 0,
#                     "isAuto": False
#                 })

#                 texts = statements[1].format(property, entity).split("|")
#                 # print(texts)
#                 usersay_data = []
#                 for text in texts:
#                     usersay_data.append({"text": text})
#                 usersay_data[1]["alias"] = "relation"
#                 usersay_data[1]["meta"] = "@relation"
#                 usersay_data[1]["userDefined"] = False
#                 usersay_data[3]["alias"] = "entity" + str(i)
#                 usersay_data[3]["meta"] = "@entity" + str(i)
#                 usersay_data[3]["userDefined"] = False
#                 userSays.append({
#                     "data": usersay_data,
#                     "isTemplate": False,
#                     "count": 0,
#                     "isAuto": False
#                 })

# intent["userSays"] = userSays
# # print(intent)
# with open("intent/relationIntent.json", "w") as json_file:
#    json.dump(intent, json_file)
