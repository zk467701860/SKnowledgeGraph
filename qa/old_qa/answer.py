class Answer:

    def __init__(self, answer_text, node_list, score, relation_list=[]):
        self.node_list = node_list  # the instances of  Node class,from py2neo import Node
        self.relation_list = relation_list  # the instances of  Relation class,from py2neo import Relation
        self.answer_text = answer_text
        self.score = score
        pass
