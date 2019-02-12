# -*- coding: utf-8 -*-
import re

import fasttext

def detailResult(modelname,testname):
    classifier = fasttext.load_model(modelname, label_prefix='__label__')
    labels_right = []
    texts = []
    with open(testname) as fr:
        for line in fr:
            line = line.decode("utf-8").rstrip()
            lines = line.split("\t")
            labels_right.append(lines[1].replace("__label__", ""))
            texts.append(line.split("\t")[0])
        #     print labels
        #     print texts
    #     break
    es = classifier.predict(texts)
    labels_predict = [e[0] for e in es]  # 预测输出结果为二维形式
    # print labels_predict

    text_labels = list(set(labels_right))
    text_predict_labels = list(set(labels_predict))
    #print text_predict_labels
    #print text_labels

    A = dict.fromkeys(text_labels, 0)  # 预测正确的各个类的数目
    B = dict.fromkeys(text_labels, 0)  # 测试数据集中各个类的数目
    C = dict.fromkeys(text_predict_labels, 0)  # 预测结果中各个类的数目
    for i in range(0, len(labels_right)):
        B[labels_right[i]] += 1
        C[labels_predict[i]] += 1
        if labels_right[i] == labels_predict[i]:
            A[labels_right[i]] += 1
        # else:
        #     print "error: " + labels_right[i], "  ", labels_predict[i], "  ", texts[i]

    print A
    print B
    print C
    # 计算准确率，召回率，F值
    for key in B:
        try:
            r = float(A[key]) / float(B[key])
            p = float(A[key]) / float(C[key])
            f = p * r * 2 / (p + r)
            print "%s:\t p:%f\t r:%f\t f:%f" % (key, p, r, f)
        except:
            print "error:", key, "right:", A.get(key, 0), "real:", B.get(key, 0), "predict:", C.get(key, 0)

fileName = ["file0.txt","file1.txt","file2.txt","file3.txt","file4.txt","file5.txt","file6.txt","file7.txt","file8.txt","file9.txt"]

for i in range(0,10):
    trainfile = open("../data/big_train.txt", "w")

    # making traning and testing file
    for j in range(0,10):
        if j!=i:
            filetmp = open("../data/" + fileName[j], "r")
            trainfile.writelines(filetmp.readlines())
            filetmp.close()
    trainfile.close()

    classifier = fasttext.supervised("../data/big_train.txt", "news_fasttext.model", label_prefix="__label__")

    result = classifier.test("../data/" +fileName[i])
    print  "----------------------------/n"

    detailResult("news_fasttext.model.bin", "../data/" +fileName[i])





