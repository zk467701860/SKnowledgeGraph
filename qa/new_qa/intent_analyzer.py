import re
from abc import ABCMeta, abstractmethod
import dialogflow
import uuid




class Answer:

    def __init__(self, answer_text, score=0.0, node=None):
        self.answer_text = answer_text
        self.score = score
        self.node = node

    def __repr__(self):
        return '<Answer: answer_text=%r score=%r node=%r>' % (
            self.answer_text, self.score, self.node)

    def __eq__(self, other):
        if isinstance(other, Answer):
            return self.answer_text == other.answer_text and self.node == other.node
        else:
            return False

    def __hash__(self):
        return hash(self.answer_text)

    def parse_json(self):
        return {
            'answer_text': self.answer_text,
            'score': self.score,
            'node': self.node
        }




class Intent:
    INTENT_TYPE_DEFAULT_INTENT = 0
    INTENT_TYPE_QUERY_SINGLE_ENTITY = 1
    INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION = 2
    INTENT_TYPE_QUERY_PROPERTY_OF_ENTITY = 3
    INTENT_TYPE_QUERY_RELATED_ENTITY = 4
    INTENT_TYPE_QUERY_BELONG_TO = 5
    INTENT_TYPE_QUERY_WHERE_TO_FIND = 6
    INTENT_TYPE_QUERY_ENTITY_WITH_FEATURE = 7
    INTENT_TYPE_QUERY_ENTITY_BY_RELATION = 8

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
        "Default Fallback Intent": Intent.INTENT_TYPE_DEFAULT_INTENT,
        "Default Welcome Intent": Intent.INTENT_TYPE_DEFAULT_INTENT,
        "Query Single Entity Intent": Intent.INTENT_TYPE_QUERY_SINGLE_ENTITY,
        "Query Library With Function Intent": Intent.INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION,
        "Query Property Of Entity Intent": Intent.INTENT_TYPE_QUERY_PROPERTY_OF_ENTITY,
        "Query Related Entity Intent": Intent.INTENT_TYPE_QUERY_RELATED_ENTITY,
        "Query Belong To Intent": Intent.INTENT_TYPE_QUERY_BELONG_TO,
        "Query Where To Find Intent": Intent.INTENT_TYPE_QUERY_WHERE_TO_FIND,

    }
    SLOT = {
        Intent.INTENT_TYPE_DEFAULT_INTENT: ["Text"],
        Intent.INTENT_TYPE_QUERY_SINGLE_ENTITY: ["Entity"],
        Intent.INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION: ["Function"],
        Intent.INTENT_TYPE_QUERY_PROPERTY_OF_ENTITY: ["Entity", "Property"],
        Intent.INTENT_TYPE_QUERY_RELATED_ENTITY: ["Entity"],
        Intent.INTENT_TYPE_QUERY_BELONG_TO: ["Entity"],
        Intent.INTENT_TYPE_QUERY_WHERE_TO_FIND: ["Entity"],

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
        text = text.replace("()", "-9-")
        text = text.replace("[]", "-10-")
        return text

    def postprocess(self, entity):
        entity = entity.replace("-1-", ".")
        entity = entity.replace("-2-", "_")
        entity = entity.replace("-3-", "(")
        entity = entity.replace("-4-", ")")
        entity = entity.replace("-5-", "<")
        entity = entity.replace("-6-", ">")
        entity = entity.replace("-7-", "[")
        entity = entity.replace("-8-", "]")
        entity = entity.replace("-9-", "()")
        entity = entity.replace("-10-", "[]")
        return entity

    def analysis_intent(self, question):
        if type(question) == str:
            question = Question(question_text=question)
        text = self.preprocess(question)
        text_input = dialogflow.types.TextInput(text=text, language_code='en')
        query_input = dialogflow.types.QueryInput(text=text_input)
        try:
            response = self.session_client.detect_intent(session=self.session, query_input=query_input)
        except Exception:
            slot_dict = {
                "Text": "Sorry, try again please."
            }
            return Intent(intent_type=Intent.INTENT_TYPE_DEFAULT_INTENT, slot_dict=slot_dict)
        if response.query_result.fulfillment_text == '':
            slot_dict = {
                "Text": "Sorry, I can't understand the question."
            }
            return Intent(intent_type=Intent.INTENT_TYPE_DEFAULT_INTENT, slot_dict=slot_dict)
        intent_type = self.INTENT_MAP[response.query_result.intent.display_name]
        values = response.query_result.fulfillment_text.split(",")
        if len(self.SLOT[intent_type]) != len(values):
            slot_dict = {
                "Text": "Sorry, I can't understand the question."
            }
            return Intent(intent_type=Intent.INTENT_TYPE_DEFAULT_INTENT, slot_dict=slot_dict)
        slot_dict = {}
        for slot, value in zip(self.SLOT[intent_type], values):
            slot_dict[slot] = self.postprocess(value)
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
            "template": "(which|Which|what|What) library is (?P<Feature>.+)",
            "slot_name_list": ["Feature", ],
            "intent_type": Intent.INTENT_TYPE_QUERY_ENTITY_WITH_FEATURE,
            "priority": 10
        },
        {
            "template": "(which|Which|what|What) (api|API) is (?P<Feature>.+)",
            "slot_name_list": ["Feature", ],
            "intent_type": Intent.INTENT_TYPE_QUERY_ENTITY_WITH_FEATURE,
            "priority": 10
        },
        {
            "template": "(which|Which) entity (?P<Relation>.+) the entity (?P<Entity>.+)",
            "slot_name_list": ["Entity", "Relation"],
            "intent_type": Intent.INTENT_TYPE_QUERY_ENTITY_BY_RELATION,
            "priority": 10
        },
        {
            "template": "(what|What) (?P<Relation>.+) the entity (?P<Entity>.+)",
            "slot_name_list": ["Entity", "Relation"],
            "intent_type": Intent.INTENT_TYPE_QUERY_ENTITY_BY_RELATION,
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
