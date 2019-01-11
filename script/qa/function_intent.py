from py2neo import Graph
import csv
import random
import json
import os


def download():
    graph = Graph(
        "http://10.141.221.75:7474",
        username="root",
        password="123456"
    )

    nodes = graph.run("MATCH (n:`awesome category`) RETURN n.name").data()
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
    return text


def process_data(nodes):
    data = [[preprocess(node["n.name"])] for node in nodes]

    with open("function/function.csv", "wb") as csv_file:
        writer = csv.writer(csv_file, dialect='excel')
        writer.writerows(data)


MAX_LINE = 30000
MAX_SIZE = 4 * 1024 * 1024


def split_file():
    file_size = os.path.getsize("function/function.csv")
    if file_size <= MAX_SIZE:
        return
    file_count = int(file_size / MAX_SIZE) + 1
    with open("function/function.csv", "r") as f:
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
            with open("function/function-{}.csv".format(i), "w") as f_small:
                f_small.write(text)


statements = [
    "which library can process |{}",
    "could you tell me the library that can process |{}",
    "please tell me the library that can process |{}",
    "which library can be used to process |{}",
    "which library can handle |{}",
    "which library can deal with |{}",
    "could you tell me the library that can handle |{}",
    "please tell me the library that can handle |{}",
    "which library can be used to process |{}",
    "could you tell me the library that can deal with |{}",
    "please tell me the library that can deal with |{}",
    "which library can be used to deal with |{}"
]

intent = {
    "name": "Query Library With Function Intent",
    "auto": True,
    "contexts": [],
    "responses": [
        {
            "resetContexts": False,
            "affectedContexts": [],
            "parameters": [
                {
                    "required": False,
                    "dataType": "@function",
                    "name": "function",
                    "value": "$function",
                    "isList": False
                }
            ],
            "messages": [
                {
                    "type": 0,
                    "speech": ["$function"]
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
    userSays = []
    funtion_count = int(MAX_USERSAY / len(statements))
    with open("function/function.csv", "r") as f:
        reader = csv.reader(f)
        functions = [row[0] for row in reader]
    for _ in range(funtion_count):
        function = random.choice(functions)
        for stmt in statements:
            texts = stmt.format(function).split("|")
            usersay_data = []
            for text in texts:
                usersay_data.append({"text": text})
            usersay_data[1]["alias"] = "function"
            usersay_data[1]["meta"] = "@function"
            usersay_data[1]["userDefined"] = False
            userSays.append({
                "data": usersay_data,
                "isTemplate": False,
                "count": 0,
                "isAuto": False
            })

    intent["userSays"] = userSays
    # print(intent)
    with open("intent/queryLibraryWithFunctionIntent.json", "w") as f:
        json.dump(intent, f)


if __name__ == "__main__":
    nodes = download()
    process_data(nodes)
    split_file()
    generate_intent()
