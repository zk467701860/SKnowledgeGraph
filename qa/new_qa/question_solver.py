from abc import ABCMeta, abstractmethod

from qa.new_qa.answer_collection import AnswerCollection
from qa.new_qa.graph_accessor_for_qa import QAGraphAccessor
from qa.new_qa.intent_analyzer import Intent, Answer
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.node_cleaner import NodeCleaner
from skgraph.graph.accessor.graph_accessor import GraphAccessor


class QuestionSolverCollectionFactory:
    def __init__(self):
        pass

    @staticmethod
    def generate_solver_collection():
        accessor = QAGraphAccessor(GraphClient(server_number=1))

        collection = QuestionSolverCollection()
        collection.add(QuestionSolverForQuerySingleEntity(graph_accessor=accessor))
        collection.add(QuestionSolverForQueryLibraryWithFunction(graph_accessor=accessor))
        collection.add(QuestionSolverForQueryPropertyOfEntity(graph_accessor=accessor))
        collection.add(QuestionSolverForQueryRelatedEntity(graph_accessor=accessor))
        collection.add(QuestionSolverForQueryBelongTo(graph_accessor=accessor))
        collection.add(QuestionSolverForQueryWhereToFind(graph_accessor=accessor))
        collection.add(QuestionSolverForQueryEntityWithFeature(graph_accessor=accessor))
        collection.add(QuestionSolverForDefalutIntent(graph_accessor=accessor))
        collection.add(QuestionSolverForQueryEntityByRelatoin(graph_accessor=accessor))
        return collection


class QuestionSolverCollection:
    def __init__(self):
        self.solver_list = []

    def add(self, solver):
        self.solver_list.append(solver)

    def solve_by_solvers(self, question_with_intent):
        for solver in self.solver_list:
            answer_collection = solver.solve(question_with_intent)
            if answer_collection:
                return answer_collection

        return None


# todo: implement more questionSolver subclass for different question
class QuestionSolver:
    __metaclass__ = ABCMeta

    def __init__(self, intent_type):
        self.intent_type = intent_type
        self.nodeCleaner = NodeCleaner()

    @abstractmethod
    def get_answer_collection(self, question_with_intent):
        return []

    def is_solvable(self, question_with_intent):
        if question_with_intent.get_intent().intent_type == self.intent_type:
            return True
        return False

    def solve(self, question_with_intent):
        if not self.is_solvable(question_with_intent):
            return []
        return self.get_answer_collection(question_with_intent)            


class QuestionSolverForQuerySingleEntity(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForQuerySingleEntity, self).__init__(Intent.INTENT_TYPE_QUERY_SINGLE_ENTITY)
        self.graph_accessor = graph_accessor
        self.entity = None

    def get_definitions_for_node(self, node):
        definition = None
        definition = node["description"]
        if "descriptions_en" in node:
            definition = node["descriptions_en"]
        return definition

    def get_definition_from_labels(self, node):
        # todo get the label from a label Util
        t = [
            ("awesome item", "library"),
            ("java abstract property", "java abstract property"),
            ("java class", "java class"),
            ("java constructor", "java constructor"),
            ("java enum", "java enum"),
            ("java field", "java field"),
            ("java library", "library"),
            ("java method", "java method"),
            ("java method parameter", "java method parameter"),
            ("java nested class", "nested class"),
            ("java package", "java package"),
            ("library", "library"),
            ("library concept", "concept about library"),
            ("platform", "computer platform"),
            ("programming language", "programming language"),
            ("programming language concept", "concept about programming language"),
            ("library concept", "concept about library"),
            ("software concept", "concept about software"),
            ("so tag", "StackOverflow tag"),
            ("alias", "alias")
        ]
        for label, text in t:
            if node.has_label(label):
                return "It is a " + text + ".\n "
        return None

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_SINGLE)

        intent = question_with_intent.intent
        self.entity = intent.get_slot_value("Entity")
        node_linking_record_list = self.graph_accessor.entity_linking_by_name_search(self.entity)
        print(node_linking_record_list)
        self.add_answer_to_list(answer_collection, node_linking_record_list)
        node_linking_record_list = self.graph_accessor.entity_linking_by_fulltext_search(self.entity)
        self.add_answer_to_list(answer_collection, node_linking_record_list)
        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        for record in node_linking_record_list:
            node = record["node"]
            all_definition = ""
            # print(node)
            # print(self.nodeCleaner.clean_labels(node))
            description_definition = self.get_definitions_for_node(node)
            label_definition = self.get_definition_from_labels(node)
            if label_definition:
                all_definition = all_definition + label_definition
            if description_definition:
                all_definition = all_definition + description_definition

            if all_definition:
                node_ = {
                    "id": GraphAccessor.get_id_for_node(node),
                    "name": self.nodeCleaner.get_clean_node_name(node),
                    "labels": self.nodeCleaner.clean_labels(node),
                }
                score = len(self.nodeCleaner.clean_node_properties(node).keys())
                if node_['name'].lower() == self.entity.lower():
                    score += 10000
                answer = Answer(answer_text=all_definition, score=score, node=node_)
                answer_collection.add(answer)


class QuestionSolverForQueryLibraryWithFunction(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForQueryLibraryWithFunction, self).__init__(Intent.INTENT_TYPE_QUERY_LIBRARY_WITH_FUNCTION)
        self.graph_accessor = graph_accessor

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_LIST)

        intent = question_with_intent.intent
        function_str = intent.get_slot_value("Function")

        node_linking_record_list = self.graph_accessor.entity_linking_by_function_search(function_str)
        self.add_answer_to_list(answer_collection, node_linking_record_list)

        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        for record in node_linking_record_list:
            node = record["node"]
            name = node["name"]
            if name:
                node_ = {
                    "id": GraphAccessor.get_id_for_node(node),
                    "name": self.nodeCleaner.get_clean_node_name(node),
                    "labels": self.nodeCleaner.clean_labels(node),
                }
                score = len(self.nodeCleaner.clean_node_properties(node).keys())
                answer = Answer(answer_text=name, score=score, node=node_)
                answer_collection.add(answer)


class QuestionSolverForQueryPropertyOfEntity(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForQueryPropertyOfEntity, self).__init__(Intent.INTENT_TYPE_QUERY_PROPERTY_OF_ENTITY)
        self.graph_accessor = graph_accessor
        self.property = None
        self.entity = None

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_SINGLE)
        intent = question_with_intent.intent
        self.entity = intent.get_slot_value("Entity")
        self.property = intent.get_slot_value("Property")
        node_linking_record_list = self.graph_accessor.entity_linking_by_name_search(self.entity)
        self.add_answer_to_list(answer_collection, node_linking_record_list)
        node_linking_record_list = self.graph_accessor.entity_linking_by_fulltext_search(self.entity)
        self.add_answer_to_list(answer_collection, node_linking_record_list)

        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        for record in node_linking_record_list:
            node = record["node"]
            if node.get(self.property) is None:
                answer = node["name"] + " has no property '" + self.property + "'."
                related_node_list = [node, ]
                answer = Answer(answer_text=answer, score=1.0, node_list=related_node_list)
                answer_collection.add(answer)
            property = node[self.property]
            if property:
                name = node['name']
                node_ = {
                    "id": GraphAccessor.get_id_for_node(node),
                    "name": self.nodeCleaner.get_clean_node_name(node),
                    "labels": self.nodeCleaner.clean_labels(node),
                }
                score = len(self.nodeCleaner.clean_node_properties(node).keys())
                if node_['name'].lower() == self.entity.lower():
                    score += 10000
                answer = Answer(answer_text=property, score=score, node=node_)
                answer_collection.add(answer)


class QuestionSolverForQueryRelatedEntity(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForQueryRelatedEntity, self).__init__(Intent.INTENT_TYPE_QUERY_RELATED_ENTITY)
        self.graph_accessor = graph_accessor

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_LIST)
        intent = question_with_intent.intent
        entity = intent.get_slot_value("Entity")
        node_linking_record_list = self.graph_accessor.search_related_entity(entity)
        self.add_answer_to_list(answer_collection, node_linking_record_list)

        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        for record in node_linking_record_list:
            node = record["node"]
            name = node["name"]
            if name:
                node_ = {
                    "id": GraphAccessor.get_id_for_node(node),
                    "name": self.nodeCleaner.get_clean_node_name(node),
                    "labels": self.nodeCleaner.clean_labels(node),
                }
                score = len(self.nodeCleaner.clean_node_properties(node).keys())
                answer = Answer(answer_text=name, score=score, node=node_)
                answer_collection.add(answer)


class QuestionSolverForQueryBelongTo(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForQueryBelongTo, self).__init__(Intent.INTENT_TYPE_QUERY_BELONG_TO)
        self.graph_accessor = graph_accessor

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_LIST)
        intent = question_with_intent.intent
        entity = intent.get_slot_value("Entity")
        node_linking_record_list = self.graph_accessor.search_entity_by_relation(entity, "belong to")
        self.add_answer_to_list(answer_collection, node_linking_record_list)

        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        for record in node_linking_record_list:
            node = record["node"]
            name = node["name"]
            if name:
                node_ = {
                    "id": GraphAccessor.get_id_for_node(node),
                    "name": self.nodeCleaner.get_clean_node_name(node),
                    "labels": self.nodeCleaner.clean_labels(node),
                }
                score = len(self.nodeCleaner.clean_node_properties(node).keys())
                answer = Answer(answer_text=name, score=score, node=node_)
                answer_collection.add(answer)


class QuestionSolverForQueryWhereToFind(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForQueryWhereToFind, self).__init__(Intent.INTENT_TYPE_QUERY_WHERE_TO_FIND)
        self.graph_accessor = graph_accessor
        self.entity = None

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_SINGLE)
        intent = question_with_intent.intent
        self.entity = intent.get_slot_value("Entity")
        node_linking_record_list = self.graph_accessor.entity_linking_by_fulltext_search(self.entity)
        self.add_answer_to_list(answer_collection, node_linking_record_list)

        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        website_property_name_list = ["source code repository", "official website", "website"]
        for record in node_linking_record_list:
            node = record["node"]
            website = None
            for website_property_name in website_property_name_list:
                if node.get(website_property_name) is not None:
                    website = node[website_property_name]
                    break
            if website:
                node_ = {
                    "id": GraphAccessor.get_id_for_node(node),
                    "name": self.nodeCleaner.get_clean_node_name(node),
                    "labels": self.nodeCleaner.clean_labels(node),
                }
                score = len(self.nodeCleaner.clean_node_properties(node).keys())
                if node_['name'].lower() == self.entity.lower():
                    score += 10000
                answer = Answer(answer_text=website, score=score, node=node_)
                answer_collection.add(answer)


class QuestionSolverForDefalutIntent(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForDefalutIntent, self).__init__(Intent.INTENT_TYPE_DEFAULT_INTENT)
        self.graph_accessor = graph_accessor

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_DEFAULT)
        intent = question_with_intent.intent
        text = intent.get_slot_value("Text")
        answer = Answer(answer_text=text, score=1.0, node=None)
        answer_collection.add(answer)
        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        pass


class QuestionSolverForQueryEntityByRelatoin(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForQueryEntityByRelatoin, self).__init__(Intent.INTENT_TYPE_QUERY_ENTITY_BY_RELATION)
        self.graph_accessor = graph_accessor

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_LIST)
        intent = question_with_intent.intent
        entity = intent.get_slot_value("Entity")
        relation = intent.get_slot_value("Relation")
        node_linking_record_list = self.graph_accessor.search_entity_by_relation(entity, relation)
        self.add_answer_to_list(answer_collection, node_linking_record_list)

        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        for record in node_linking_record_list:
            node = record["node"]
            name = node["name"]
            if name:
                node_ = {
                    "id": GraphAccessor.get_id_for_node(node),
                    "name": self.nodeCleaner.get_clean_node_name(node),
                    "labels": self.nodeCleaner.clean_labels(node),
                }
                score = len(self.nodeCleaner.clean_node_properties(node).keys())
                answer = Answer(answer_text=name, score=score, node=node_)
                answer_collection.add(answer)


class QuestionSolverForQueryEntityWithFeature(QuestionSolver):
    def __init__(self, graph_accessor):
        super(QuestionSolverForQueryEntityWithFeature, self).__init__(Intent.INTENT_TYPE_QUERY_ENTITY_WITH_FEATURE)
        self.graph_accessor = graph_accessor

    def get_answer_collection(self, question_with_intent):
        answer_collection = AnswerCollection(AnswerCollection.ANSWER_TYPE_LIST)
        intent = question_with_intent.intent
        feature = intent.get_slot_value("Feature")
        node_linking_record_list = self.graph_accessor.search_entity_by_feature(feature)
        self.add_answer_to_list(answer_collection, node_linking_record_list)

        return answer_collection

    def add_answer_to_list(self, answer_collection, node_linking_record_list):
        for record in node_linking_record_list:
            node = record["node"]
            name = node["name"]
            if name:
                node_ = {
                    "id": GraphAccessor.get_id_for_node(node),
                    "name": self.nodeCleaner.get_clean_node_name(node),
                    "labels": self.nodeCleaner.clean_labels(node),
                }
                score = len(self.nodeCleaner.clean_node_properties(node).keys())
                answer = Answer(answer_text=name, score=score, node=node_)
                answer_collection.add(answer)
