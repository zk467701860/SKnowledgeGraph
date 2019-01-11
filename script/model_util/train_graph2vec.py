from model_util.graph_vector.node2vec import GraphNode2Vec
from skgraph.graph.accessor.graph_accessor import GraphClient

if __name__ == "__main__":
    output_path = 'graph_vector.plain.txt'
    graph_client = GraphClient(server_number=4)
    graphNode2Vec = GraphNode2Vec(graph_client.graph)

    model = graphNode2Vec.start_train_graph_vector(output_path)
    print("training graph vector complete")

    cos = model.wv.similarity(str(524), str(482))
    print("similarity between 524 and 482 = %f" % cos)

    cos = model.wv.similarity(str(9264), str(482))
    print("similarity between 9264 and 482 = %f" % cos)
