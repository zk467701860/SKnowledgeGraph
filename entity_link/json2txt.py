# -*- coding: utf-8 -*-
import json
import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

with open("raw_data/html.json", "r") as f:
    data = json.load(f)
with open("raw_data/train_data.txt", "w") as f:
    for ele in data:
        f.write(ele['clean_text'])
        f.write('\n')
