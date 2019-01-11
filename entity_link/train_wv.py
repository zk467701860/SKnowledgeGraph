# -*- coding: utf-8 -*-
from fastText import FastText 

model = FastText.train_unsupervised('raw_data/train_data.txt')
model.save_model('wv/model.bin')
