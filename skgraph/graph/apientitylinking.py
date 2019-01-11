import re

import tagme

from accessor.graph_accessor import DefaultGraphAccessor, GraphClient

tagme.GCUBE_TOKEN = "a935e949-d3ba-4946-b54f-9ac267b28e33-843339462"
tagme.DEFAULT_TAG_API = "https://wat.d4science.org/wat/tag/tag"


class APIEntityLinking:
    pattern1 = re.compile(r'\w*[A-Z]+\w+')
    pattern2 = re.compile(r'(\w+\.)+\w+')
    pattern3 = re.compile(r'(\w+\.)+\w+(\(.*?\))')
    pattern4 = re.compile(r'(\w+) (object|class|interface|method|package|exception|error)')
    stopWords = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost",
                 "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst",
                 "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
                 "around", "as", "at", "back", "be", "became", "because", "become", "becomes", "becoming", "been",
                 "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill",
                 "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry",
                 "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either",
                 "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
                 "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first",
                 "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further",
                 "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
                 "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however",
                 "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep",
                 "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile",
                 "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself",
                 "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
                 "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto",
                 "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per",
                 "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems",
                 "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so",
                 "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such",
                 "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence",
                 "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv",
                 "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to",
                 "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up",
                 "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence",
                 "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
                 "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
                 "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

    def __init__(self):
        # self.graph_accessor = DefaultGraphAccessor(GraphClient(server_number=1))
        # self.alias_graph_accessor = DefaultGraphAccessor(GraphClient(server_number=3))
        self.graph_accessor = None
        self.alias_graph_accessor = None

    def get_link(self, text=""):
        searchObject1 = re.finditer(APIEntityLinking.pattern1, text)
        searchObject2 = re.finditer(APIEntityLinking.pattern2, text)
        searchObject3 = re.finditer(APIEntityLinking.pattern3, text)
        searchObject4 = re.finditer(APIEntityLinking.pattern4, text)

        graph_client = self.graph_accessor
        name = []
        ret = []

        if searchObject1:
            for m in searchObject1:
                result = m.group()
                if result not in name and result.lower() not in APIEntityLinking.stopWords:
                    node = self.alias_graph_accessor.find_one_by_name_property("api", result)
                    if node:
                        link_id = node["link_id"][0]
                        node_name = self.graph_accessor.get_node_name_by_id(link_id)
                        if node_name:
                            name.append(node_name)
                            ret.append({"startPOS": m.start(),
                                        "endPOS": m.end(),
                                        "Str": node_name,
                                        "type": "api",
                                        "url": "http://bigcode.fudan.edu.cn/Entity/" + str(link_id)})

        searchObject_list = [searchObject2, searchObject3, searchObject4]
        for searchObject in searchObject_list:
            if searchObject:
                for m in searchObject:
                    result = m.group()
                    if result not in name:
                        node = self.alias_graph_accessor.find_one_by_name_property("api", result)
                        if node:
                            link_id = node["link_id"][0]
                            node_name = self.graph_accessor.get_node_name_by_id(link_id)
                            if node_name:
                                name.append(node_name)
                                ret.append({"startPOS": m.start(),
                                            "endPOS": m.end(),
                                            "Str": node_name,
                                            "type": "api",
                                            "url": "http://bigcode.fudan.edu.cn/Entity/" + str(link_id)})

        lunch_annotations = tagme.annotate(text)

        # Print annotations with a score higher than 0.1
        for ann in lunch_annotations.get_annotations(0.3):
            if ann.mention not in name:
                wikipedia_url = tagme.title_to_uri(ann.entity_title)
                node = graph_client.get_node_by_wikipedia_link(wikipedia_url)
                if node:
                    if node["name"] not in name:
                        name.append(node["name"])
                        ret.append({"startPOS": ann.begin, "endPOS": ann.end, "Str": node["name"], "type": "concept",
                                    "url": "http://bigcode.fudan.edu.cn/Entity/" + str(
                                        graph_client.get_id_for_node(node))})
                else:
                    name.append(ann.mention)
                    ret.append({"startPOS": ann.begin, "endPOS": ann.end, "Str": ann.mention, "type": "concept",
                                "url": wikipedia_url})

        return ret
