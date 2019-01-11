# coding=utf-8
import re
import time

from nltk.stem import WordNetLemmatizer
from pattern.text import parsetree


class EntityExtractor:
    MAX_STRING_LEN = 60
    MAX_WORD_NUM = 8
    invalid_content = [
        "0x",
        "|",
        "^ ",
        "_ ",
        ":[ ",
        "\u",
        "\u",
        "<",
        ">",
        "</",
        "/>",
        "//",
        "::",
    ]
    VALID_CHAR_STRING = "qwertyuiopasdfghjklzxcvbnm./1234567890()@_<>/- "

    def __init__(self):

        self.stopWords = {'ourselves', 'first', 'single', 'hers', 'between', 'yourself', 'but', 'again', 'there',
                          'about', 'once', 'one', 'two', 'three', 'second', 'new', 'multiple', 'most', 'mostly',
                          'exact', 'enough', 'entire',
                          'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be',
                          'some', ' for', 'do',
                          'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am',
                          'or', 'who', 'as', 'from ', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are',
                          'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself',
                          'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours',
                          'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been',
                          'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over',
                          'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just',
                          'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being',
                          'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here',
                          'than', "something", "anything",

                          "also", "already", "another", "although", "always", "am", "among",

                          "amongst", "anybody", "any", "anymore", "anyway", "apparently", "both", "better", "best",
                          "by", "but", "considering", "corresponding", "containing", "do", "does", "did", "each",
                          "else", "elsewhere", "enough", "even", "evenly", "ever", "every", "everybody", "everyone",
                          "everything", "everywhere", "f", "except", "e.g", "e", "far", "few", "little", "no", "first",
                          "five", "one", "two", "three", "four", "five", "1th", "six", "seven", "eight", "nine", "ten",
                          "2th", "3th", "4th", "5th", "following", "followed", "former", "furthermore",

                          "her",
                          "here",
                          "hers",
                          "herself",
                          "hes",
                          "hi",
                          "hid",
                          "high",
                          "higher",
                          "highest",
                          "him",
                          "himself",
                          "his",
                          "hither",

                          "how",

                          "however",
                          "hundred",
                          "of",

                          "if",
                          "im",
                          "immediate",
                          "immediately",
                          "importance",
                          "important",
                          "in",
                          "inner",
                          "insofar",
                          "instead",
                          "interest",
                          "interested",
                          "interesting",
                          "interests",
                          "into",
                          "inward",
                          "is",
                          "isn't",
                          "it",
                          "it'd",
                          "it'll",
                          "it's",
                          "itd",
                          "its",
                          "itself",
                          "latest", "last", "many", "maybe", "merely", "me", "more", "much", "new", "nearly", "never",
                          "must", "next", "nobody", "nor", "none", "now", "one", "ones", "once", "only", "old", "on",
                          "of", "often", "or", "our", "other", "others", "our", "ours", "over", "own", "your", "my",
                          "mine", "yours", "per",
                          "such", "still", "that", "those", "their", "theirs", "then", "there", "them", "themselves",
                          "these", "those", "thereby", "though", "through", "together", "today", "well", "bad", "good",
                          "what", "when", "which", "whatever", "whenever", "when", "whether", "while", "whos", "who",
                          "whom", "whin", "yourself", "yet", "b", "c", "d", "e", "f", "zzz", "zzzz", "yes", "xxx",
                          "quite", "rather", "same", "different", "secondly", "shall", "sometime", "someone",
                          "somewhere", "somehow", "somebody", "some", "so", "aa", "aaa", "bbb", "a1", "a2", "b1", "b2",
                          "-", "a3", "abcd", "non",
                          "change", "current", "currently", "explicitly", "get", "set", "return", "access", "future",
                          "use", "using",
                          }

        self.lemmatizer = WordNetLemmatizer()

    def extract_chunk(self, text):
        """
        return all the chunk extracted form the text
        :param text: the text
        :return: list of chunk of object pattern.text.Chunk
        """
        result = []
        pst = parsetree(text)
        for sentence in pst:
            for chunk in sentence.chunks:
                if chunk.type == "NP":
                    result.append(chunk)
                    # print chunk.type, [(w.string, w.type) for w in chunk.words]
        return result

    def filter_chunk(self, chunk_list):
        """
        return all the chunk extracted form the text
        :param text: the text
        :return: list of chunk of object pattern.text.Chunk
        """
        result = []

        for chunk in chunk_list:
            # print(chunk.words[0])
            # if chunk.words[0].string=="The":
            #     chunk.words.remove(chunk.words[0])
            if self.is_valid_chunk_string(chunk.string):
                result.append(chunk)
        return result

    def is_valid_chunk_string(self, chunk_string):
        if chunk_string == "" or chunk_string == None:
            return False
        chunk_string = chunk_string.lower()

        if chunk_string in self.stopWords:
            return False
        for char in chunk_string:
            if char not in self.VALID_CHAR_STRING:
                return False
        if len(chunk_string.split(" ")) >= self.MAX_WORD_NUM:
            return False
        if chunk_string.endswith(".") and len(chunk_string) == 2:
            return False
        if len(chunk_string) > self.MAX_STRING_LEN or len(chunk_string) <= 2:
            return False

        if "https://" in chunk_string or "http://" in chunk_string:
            return False

        if "(" in chunk_string and ")" not in chunk_string:
            return False
        if ")" in chunk_string and "(" not in chunk_string:
            return False
        for invalid in self.invalid_content:
            if invalid in chunk_string:
                return False
        for word in chunk_string.replace(".", " ").replace("x", " ").split(" "):
            if word.isdigit():
                return False
        return True

    # print(chunk.string+" not in stopwords")
    def lemmatize_chunk(self, chunk_string):
        words = chunk_string.split(" ")
        new_words = []
        for word in words:
            new_words.append(self.lemmatizer.lemmatize(word))

        return " ".join(new_words)

    def get_clean_entity_name_for_string(self, chunk_string):
        """
        get the valid entity name, for example, "an Activity"=>"Activity","activities"=>"activity"
        :param chunk_string:
        :return: None, the cleaned entity name can be got. otherwise, return the clean entity
        """

        if self.is_valid_chunk_string(chunk_string) == False:
            return None
        return self.clean_np_text(chunk_string)

    def extract_chunks_strings(self, text):
        if text == "" or text == None:
            return []
        chunk_list = self.extract_chunk(text)
        chunk_list = self.filter_chunk(chunk_list)
        chunk_strings = [chunk.string for chunk in chunk_list]
        return list(set(chunk_strings))

    def extract_clean_entity_name_from_text(self, text):
        chunk_list = self.extract_chunks_strings(text)
        entity_name_list = []
        for chunk in chunk_list:
            entity_name = self.get_clean_entity_name_for_string(chunk)
            if entity_name:
                entity_name_list.append(entity_name)
        return list(set(entity_name_list))

    def is_valid_date(self, input_str):
        """
        Determine if it is a valid date string
        """
        word_list = input_str.split(' ', 1)
        for w in word_list:
            try:
                if ":" in w:
                    time.strptime(w, "%Y-%m-%d %H:%M:%S")
                else:
                    time.strptime(w, "%Y-%m-%d")
                return True
            except:
                pass
        return False

    def is_link_by_num(self, np_text):
        pattern = re.compile(r'(\d+)-(\d+)')
        m = pattern.findall(np_text)
        if m is None or len(m) == 0:
            return False

        return True

    def remove_start_or_end_stop_word_for_one_time(self, np_text):
        word_list = np_text.lower().split(' ')
        if word_list[0] in self.stopWords:
            word_list = word_list[1:]
        if len(word_list) == 0:
            return None
        if word_list[-1] in self.stopWords:
            word_list = word_list[:-1]
        if len(word_list) == 0:
            return None

        return " ".join(word_list)

    def remove_start_dot(self, np_text):
        while len(np_text) > 0 and np_text[0] == '.':
            np_text = np_text[1:]
        return np_text

    def remove_other_start(self, np_text):
        if np_text.find('0x') == 0 or np_text.find('/ ') == 0 or np_text.find('1/') == 0:
            return True
        return False

    def end_with_point(self, np_text):
        if np_text[-1] == '.':
            return np_text[0:-1]
        return np_text

    def remove_all_stop_words_in_start_and_end(self, np_text):
        while True:
            new_np_text = self.remove_start_or_end_stop_word_for_one_time(np_text)
            if new_np_text == None:
                return None

            if np_text == new_np_text:
                return np_text
            np_text = new_np_text

    def clean_np_text(self, np_text):

        np_text = np_text.lower()
        '''
        eg: merge
        3166-1 two-letter country code
        3166-1 two letters country code
        to lower case
        start with stop word
        remove ‘-’
        lemmatize_chunk
        '''
        np_text = self.remove_start_dot(np_text)
        np_text = self.end_with_point(np_text)
        if np_text.isspace():
            return None
        if self.remove_other_start(np_text):
            return None
        is_valid_date = self.is_valid_date(np_text)
        np_text = self.lemmatize_chunk(np_text)
        is_link_by_num = self.is_link_by_num(np_text)
        if is_valid_date or is_link_by_num:
            return None
        np_text = self.remove_all_stop_words_in_start_and_end(np_text)
        if np_text == None:
            return None
        words = np_text.split(" ")
        if np_text[0] == "@" and len(words) >= 2:
            np_text = words[0] + " ".join(words[1:])
        if np_text == "extended data":
            np_text = "data"
        np_text = np_text.replace("-", " ")
        return np_text

    def extract_single_verb(self, text):
        """
        return all the chunk extracted form the text
        :param text: the text
        :return: list of chunk of object pattern.text.Chunk
        """
        result = []
        pst = parsetree(text)
        for sentence in pst:
            for chunk in sentence.chunks:
                if chunk.type == "VP":
                    result.append(chunk.string.split(" ")[0])

        candidates = set(result)

        final_result = []
        for candidate in candidates:
            candidate = self.lemmatizer.lemmatize(candidate)
            if candidate not in self.stopWords:
                final_result.append(candidate)

        return list(set(final_result))

    def extract_verb_and_entity_name_from_text(self, text):

        verb_result = []
        np_result = []

        pst = parsetree(text)
        for sentence in pst:
            for chunk in sentence.chunks:
                if chunk.type == "NP":
                    np_result.append(chunk)
                    continue
                if chunk.type == "VP":
                    word_tagged_list = chunk.tagged
                    for word in word_tagged_list:
                        if word[1][0] == "V":
                            verb_result.append(word[0])
                    continue

        verb_result = set(verb_result)

        final_result = []
        for candidate in verb_result:
            candidate = self.lemmatizer.lemmatize(candidate)
            if candidate not in self.stopWords:
                final_result.append(candidate)

        for np in np_result:
            entity_name = self.get_clean_entity_name_for_string(np.string)
            if entity_name:
                final_result.append(entity_name)

        return list(set(final_result))

    def expand_the_chunk_by_words(self, final_chunk_list):
        final_set = []
        for chunk in final_chunk_list:
            final_set.append(chunk)
            for word in chunk.split(" "):
                if word not in self.stopWords:
                    final_set.append(word)
        print("word set", final_set)
        return list(set(final_set))

    def get_all_possible_key_word_from_text(self, text):
        key_words_list = self.extract_verb_and_entity_name_from_text(text)
        whole_words = " ".join(key_words_list)

        final_key_words_list = self.expand_the_chunk_by_words(key_words_list)
        final_key_words_list.append(whole_words)
        return final_key_words_list
