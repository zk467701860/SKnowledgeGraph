# from google.cloud import storage
import dialogflow
import uuid
import os
import re
from abc import ABCMeta, abstractmethod

# todo change the path for json to relative
# add library to requirements.txt

file_dir = os.path.split(os.path.realpath(__file__))[0]
file_name = 'SKnowledge-8e55dec4e266.json'
full_path = os.path.join(file_dir, file_name)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = full_path


class Intent:
    INTENT_TYPE_QUERY_SINGLE_ENTITY = 1
    INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION = 2

    def __init__(self, intent_type, slot_dict):
        self.intent_type = intent_type
        self.slot_dict = slot_dict

    def __repr__(self):
        return '<Intent: intent_type=%r slot_dict=%r>' % (self.intent_type, self.slot_dict)

    def get_slot_value(self, slot):
        if slot in self.slot_dict:
            return self.slot_dict[slot]
        return None


class Question:
    def __init__(self, question_text):
        self.question_text = question_text

    def __repr__(self):
        return '<Question: question_text=%r >' % (self.question_text,)


class QuestionWithIntent:
    def __init__(self, question, intent):
        self.question = question
        self.intent = intent

    def get_intent(self):
        return self.intent

    def __repr__(self):
        return '<QuestionWithIntent: question=%r intent=%r>' % (self.question, self.intent)


class IntentAnalyzer:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def analysis_intent(self, question):
        return None

    def generate_question_with_intent(self, question):
        intent = self.analysis_intent(question)
        if intent:
            return QuestionWithIntent(question=question, intent=intent)
        return None


# todo: implement a IntentAnalyzer for calling dialogflow service
class TemplateIntentAnalyzer(IntentAnalyzer):
    def __init__(self):
        super(TemplateIntentAnalyzer, self).__init__()
        self.template_list = TemplateGenerator().generate_all()

    def analysis_intent(self, question):
        if type(question) == str:
            question = Question(question_text=question)
        for matcher in self.template_list:
            intent = matcher.get_intent(question.question_text)
            if intent:
                return intent

        return None


class DialogflowIntentAnalyzer(IntentAnalyzer):
    INTENT_MAP = {
        "querySingleEntity": Intent.INTENT_TYPE_QUERY_SINGLE_ENTITY,
        "queryLibraryWithFunction": Intent.INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION
    }
    SLOT_NAME = {
        Intent.INTENT_TYPE_QUERY_SINGLE_ENTITY: "Entity",
        Intent.INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION: "Function"
    }

    def __init__(self):
        super(DialogflowIntentAnalyzer, self).__init__()
        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path('sknowledge-7d6fe', uuid.uuid1())

    def preprocess(self, question):
        text = question.question_text.strip().rstrip(".?!")
        text = text.replace(".", "-1-")
        text = text.replace("_", "-2-")
        text = text.replace("(", "-3-")
        text = text.replace(")", "-4-")
        text = text.replace("<", "-5-")
        text = text.replace(">", "-6-")
        text = text.replace("[", "-7-")
        text = text.replace("]", "-8-")
        return text

    def postprocess(self, entity):
        entity = entity.replace("-1-", ".")
        entity = entity.replace("-2-", "_")
        entity = entity.replace("-3-", "(")
        entity = entity.replace("-1-", ")")
        entity = entity.replace("-2-", "<")
        entity = entity.replace("-3-", ">")
        entity = entity.replace("-1-", "[")
        entity = entity.replace("-2-", "]")
        return entity

    def analysis_intent(self, question):
        if type(question) == str:
            question = Question(question_text=question)
        text = self.preprocess(question)
        text_input = dialogflow.types.TextInput(text=text, language_code='en')
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = self.session_client.detect_intent(session=self.session, query_input=query_input)
        intent_type = self.INTENT_MAP[response.query_result.intent.display_name]
        slot_dict = {
            self.SLOT_NAME[intent_type]: self.postprocess(response.query_result.fulfillment_text)
        }
        return Intent(intent_type=intent_type, slot_dict=slot_dict)


class TemplateMatcher:
    def __init__(self, regex_template, slot_name_list, intent_type, priority):
        self.regex_template = regex_template
        self.slot_name_list = slot_name_list
        self.pattern = re.compile(self.regex_template)
        self.intent_type = intent_type
        self.priority = priority

    def is_valid_query(self, query):
        if not query:
            return False
        return True

    def clean_query(self, query):
        return query.strip().strip("?").strip(".").strip()

    def get_slot_dict(self, query):
        if not self.is_valid_query(query):
            return None
        query = self.clean_query(query)
        result = re.match(self.pattern, query)
        if result is None:
            return None
        parameter_dict = result.groupdict()
        return parameter_dict

    def get_intent(self, query):
        slot_dict = self.get_slot_dict(query)
        if slot_dict is None:
            return None

        return Intent(intent_type=self.intent_type, slot_dict=slot_dict)


class TemplateGenerator:
    TEMPLATE_META_DATA = [
        {
            "template": "(what|What) (is|are) (?P<Entity>.+)",
            "slot_name_list": ["Entity", ],
            "intent_type": Intent.INTENT_TYPE_QUERY_SINGLE_ENTITY,
            "priority": 10
        },
        {
            "template": "(which|Which) library can (?P<Function>.+)",
            "slot_name_list": ["Function", ],
            "intent_type": Intent.INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION,
            "priority": 10
        },
    ]

    def __init__(self):
        pass

    def generate_all(self):
        matcher_list = []
        for temp in self.TEMPLATE_META_DATA:
            matcher_list.append(
                TemplateMatcher(regex_template=temp["template"],
                                slot_name_list=temp["slot_name_list"],
                                intent_type=temp["intent_type"],
                                priority=temp["priority"]))

        # sort by the priority
        matcher_list.sort(key=lambda x: x.priority, reverse=True)
        return matcher_list


if __name__ == "__main__":
    analyzer = DialogflowIntentAnalyzer()

    while True:
        usersay = raw_input('input:\n')
        question = Question(usersay)
        # print(question_text)
        question_with_intent = analyzer.generate_question_with_intent(question)
        # print(usersay)
        print(question_with_intent.get_intent())
