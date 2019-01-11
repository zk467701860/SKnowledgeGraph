#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 本文档提供node2vec相关操作类,读取图数据库的关系列表并且存储为.edgelist文件。
import traceback

import networkx as nx
from gensim.models import Word2Vec
from py2neo import Graph

from model_util.graph_vector import graph_for_node2vec


class GraphNode2Vec:
    def __init__(self, graph=None):
        if isinstance(graph, Graph):
            self._graph = graph

    @property
    def graph(self):
        return self._graph

    def initGraph(self, relationship_list):
        node_num = self.getNumofNode()
        print(node_num)
        G = nx.DiGraph()
        G.add_nodes_from(range(0, node_num[0]["count(*)"]))
        G.add_edges_from(relationship_list)
        return G

    def getNumofNode(self):
        try:
            query = "MATCH (n:entity) RETURN count(*)"
            return self._graph.data(query)
        except Exception as error:
            return 0

    def getAllRelationship(self):
        try:
            query = 'MATCH (n:entity)-[r]->(m:entity) RETURN id(n),id(m),type(r)'
            result = self._graph.data(query)
            relationship_list = []
            relation_type = []
            for line in result:
                if line["type(r)"] not in relation_type:
                    index = len(relation_type)
                    relation_type.append(line["type(r)"])
                else:
                    index = relation_type.index(line["type(r)"])
                relationship_list.append((line["id(n)"], line["id(m)"], {"weight": 1, "type": index}))
            return relationship_list, relation_type
        except Exception as error:
            traceback.print_exc()
            return [], []

    def trainEdgeList(self, list, output, dimensions=128, window_size=10, num_walks=20,
                      walk_length=100, workers=2, iter=20):
        nx_G = self.initGraph(list)
        G = graph_for_node2vec.GraphForNode2Vec(nx_G)
        G.preprocess_transition_probs()
        walks = G.simulate_walks(num_walks, walk_length)

        walks = [[str(item) for item in walk] for walk in walks]
        model = Word2Vec(walks, size=dimensions, window=window_size, min_count=0, sg=1, workers=workers,
                         iter=iter)

        model.save(output + ".gensim.model")
        model.wv.save_word2vec_format(output, binary=True)

        return model

    def start_train_graph_vector(self, output, dimensions=128, num_walks=20, walk_length=100, iter=10):
        list, type_list = self.getAllRelationship()
        return self.trainEdgeList(list, output, dimensions=dimensions, num_walks=num_walks, walk_length=walk_length,
                                  iter=iter)
