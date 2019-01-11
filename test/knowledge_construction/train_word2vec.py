# coding=utf-8
import multiprocessing
import time

from gensim.models import Word2Vec

if __name__ == "__main__":
    text_list = [
        '''Provides classes and interfaces for handling text, dates, numbers, and messages in a manner independent of natural languages. This means your main application or applet can be written to be language-independent, and it can rely upon separate, dynamically-linked localized resources. This allows the flexibility of adding localizations for new localizations at any time. These classes are capable of formatting dates, numbers, and messages, parsing; searching and sorting strings; and iterating over characters, words, sentences, and line breaks. This package contains three main groups of classes and interfaces: Classes for iteration over text Classes for formatting and parsing Classes for string collation ''',
        '''Provides classes and interfaces for parsing and managing certificates, certificate revocation lists (CRLs), and certification paths. It contains support for X.509 v3 certificates and X.509 v2 CRLs. Package Specification Java™ Cryptography Architecture (JCA) Reference Guide RFC 5280: Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile RFC 2560: X.509 Internet Public Key Infrastructure Online Certificate Status Protocol - OCSP Java™ Cryptography Architecture Standard Algorithm Name Documentation Related Documentation For information about X.509 certificates and CRLs, please see: http://www.ietf.org/rfc/rfc5280.txt Java™ PKI Programmer's Guide X.509 Certificates and Certificate Revocation Lists (CRLs) '''

        ]
    sentences = [text.split(" ") for text in text_list]
    model = Word2Vec(sentences, size=128, window=10, min_count=1, sg=1, hs=1, workers=multiprocessing.cpu_count())
    print("end time {}".format(time.asctime(time.localtime(time.time()))))
    print(model.wv)
    print(model.wv.vocab)
    model.save("./model/Word2Vec.test.model")
    model.wv.save("./model/vocab.test.txt")
    model.wv.save_word2vec_format("./model/vocab.test.plain.txt",binary=False)