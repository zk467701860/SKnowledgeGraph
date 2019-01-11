# coding=utf-8

from gensim.models import Word2Vec, KeyedVectors

if __name__ == "__main__":
    model = Word2Vec.load("./model/Word2Vec.test.model")
    print(model["and"])

    wv_from_text = KeyedVectors.load("./model/vocab.test.txt")  # C text format
    print(wv_from_text["and"])

    wv_from_text = KeyedVectors.load_word2vec_format("./model/vocab.test.plain.txt",
                                                     binary=False)  # C text format
    print(wv_from_text["and"])
