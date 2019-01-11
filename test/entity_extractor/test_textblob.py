from unittest import TestCase

from pattern.text import parsetree
from textblob import TextBlob, Blobber
from textblob.en.np_extractors import ConllExtractor

from entity_extractor.extractor import EntityExtractor


class TestTextBlob(TestCase):
    text_list = [
        u"The classes in this package are used for development of accessibility service that provide alternative or augmented feedback to the user.",

        u"Contains resource classes used by applications included in the platform and defines application permissions for system features.",

        u"Provides device administration features at the system level, allowing you to create security-aware applications that are useful in enterprise settings, in which IT professionals require rich control over employee devices.",

        u"Contains the backup and restore functionality available to applications. If a user wipes the data on their device or upgrades to a new Android-powered device, all applications that have enabled backup can restore the user's previous data when the application is reinstalled.",

        u"Contains high-level classes encapsulating the overall Android application model.",

        u"An Android application is defined using one or more of Android's four core application components. Two such application components are defined in this package: Activity and Service. The other two components are from the android.content package: BroadcastReceiver and ContentProvider.",

        u"An Activity is an application component that provides a screen with which users can interact in order to do something, such as dial the phone, take a photo, send an email, or view a map. An activity can start other activities, including activities that live in separate applications.",

    ]

    def test_get_np_for_default(self):
        text_list = self.text_list

        for text in text_list:
            b = TextBlob(text)
            print(b.noun_phrases)
            print(b.parse())

    def test_get_np_for_CONLLExtractor(self):
        text_list = self.text_list

        from textblob.taggers import NLTKTagger
        from textblob.tokenizers import SentenceTokenizer
        chunker = ConllExtractor()

        tb = Blobber(pos_tagger=NLTKTagger(), tokenizer=SentenceTokenizer(), np_extractor=chunker)

        for text in text_list:
            b = tb(text)
            print(b.noun_phrases)
            print(b.parse())

    def test_get_np_for_all(self):
        text_list = self.text_list

        from textblob.taggers import NLTKTagger
        from textblob.tokenizers import SentenceTokenizer
        chunker = ConllExtractor()

        tb = Blobber(pos_tagger=NLTKTagger(), tokenizer=SentenceTokenizer(), np_extractor=chunker)

        for text in text_list:
            # tbinstance=tb(text)
            # sentences=tbinstance.sentences
            # print(sentences)
            # for s in sentences:
            #     s.
            pst = parsetree(text)
            print(pst)
            for sentence in pst:
                for chunk in sentence.chunks:
                    if chunk.type == "NP":
                        print chunk.type, [(w.string, w.type) for w in chunk.words]

    def test_get_np_for_customer(self):

        text_list = self.text_list
        extractor = EntityExtractor()
        for text in text_list:
            chunk_list = extractor.extract_chunk(text)
            # for chunk in chunk_list:
            # print(chunk.string)
            chunk_list = extractor.filter_chunk(chunk_list)
            for chunk in chunk_list:
                print("NP:" + chunk.string)
                print("lemma:" + extractor.lemmatize_chunk(chunk.string))
    def test_get_clean_entity_name(self):
        text_list=["The String class represents character strings.","Note that all the *.jar and *.apk files from dexPath might be first extracted in-memory before the code is loaded. "]
        extractor = EntityExtractor()
        for text in text_list:
            chunk_names = extractor.extract_chunks_strings(text)

            for chunk in chunk_names:
                print("chunk:" + chunk)

            entity_names = extractor.extract_clean_entity_name_from_text(text)

            for entity_name in entity_names:
                print("NP:" + entity_name)
    def test_get_chunk_strings(self):
        text_list = self.text_list
        extractor = EntityExtractor()
        for text in text_list:
            chunk_list = extractor.extract_chunks_strings(text)
            for chunk in chunk_list:
                print("NP:" + chunk)
                print("lemma:" + extractor.lemmatize_chunk(chunk))
