#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import random
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import xml.dom.minidom


domTree = xml.dom.minidom.parse("../data/directives.xml")
dataset = domTree.getElementsByTagName("dataset")[0]


fileName = ["file0.txt","file1.txt","file2.txt","file3.txt","file4.txt","file5.txt","file6.txt","file7.txt","file8.txt","file9.txt"]
files = []

for str in fileName:
    filetmp = open("../data/"+str,"w")
    files.append(filetmp)

#directive data
for group in dataset.getElementsByTagName("group"):
    name = group.getAttribute("name").replace(" ","")
    # if name=="StateDirective":
    #     name = "MethodCallDirective"
    # elif name == "SynchronizationDirective":
    #     name = "MiscellaneousDirective"
    # elif name == "AlternativeDirective":
    #     name = "MiscellaneousDirective"

    directives = group.getElementsByTagName("directive")
    randomList = []
    for i in range(0,directives.length):
        randomList.append(0);

    for i in range(1, 10):
        j=0
        while j < directives.length / 10:
            tmp = random.randint(0, directives.length - 1)
            if randomList[tmp] ==0:
                randomList[tmp] = i
                j = j+1

    i = 0;
    for directive in directives:
        kind = directive.getAttribute("kind").replace(" ", "").decode("utf-8").encode("utf-8")
        line = " "+(directive.firstChild.wholeText.strip())
        line = line.decode("utf-8").encode("utf-8")
        line = line.replace("\t"," ").replace("\n"," ")
        line = line + "\t__label__" + kind + "\n"
        line = line.decode("utf-8").encode("utf-8")
        files[randomList[i]].write(line)
        i = i+1

#non-directive data
nondir = open("../data/dataset.json","r")
nondirjson = json.load(nondir)

nontext = []
for tmp in nondirjson:
    if tmp['label'] == 0 or tmp['label'] == 1:
        line = tmp['text'].decode("utf-8").encode("utf-8")
        line = line.replace("\t", " ").replace("\n", " ")
        line = line + "\t__label__" + "nonDir" + "\n"
        line = line.decode("utf-8").encode("utf-8")
        nontext.append(line)

randomList = []
for i in range(0, len(nontext)):
    randomList.append(-1);

for i in range(0, 10):
    j = 0
    while j < 200:
        tmp = random.randint(0, len(nontext) - 1)
        if randomList[tmp] == -1:
            randomList[tmp] = i
            j = j + 1

i = 0;
for l in nontext:
    if randomList[i]!=-1:
        files[randomList[i]].write(l)
    i = i + 1


nondir.close()

for f in files:
    f.close()