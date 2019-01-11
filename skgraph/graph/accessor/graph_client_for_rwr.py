from py2neo import Relationship

from factory import NodeBuilder
from graph_accessor import GraphAccessor


class RandomWalkGraphAccessor(GraphAccessor):
    def create_random_walk_similarity_by_transaction(self, random_walk_similarity_list):
        '''
        :param random_walk_similarity_list: is a list, each is a json,stand for the random walk similarity.

        example: [{"start_link_id": 4, "end_link_id": 6, "count": 0.1},
                                   {"start_link_id": 4, "end_link_id": 7, "count": 0.1}]
        :return: the response
        '''

        link_id_list = []
        for random_walk_similarity in random_walk_similarity_list:
            link_id_list.append(random_walk_similarity["start_link_id"])
            link_id_list.append(random_walk_similarity["end_link_id"])
        link_id_list = list(set(link_id_list))

        entity_node_map = {}
        graph = self.get_graph_instance()
        transaction = graph.begin()
        for link_id in link_id_list:
            entity_node = NodeBuilder().add_label("Entity").add_one_property("link_id", link_id).build()
            transaction.merge(entity_node)
            entity_node_map[str(link_id)] = entity_node

        new_random_walk_similarity_list = []
        for random_walk_similarity in random_walk_similarity_list:
            start_link_id = str(random_walk_similarity["start_link_id"])
            end_link_id = str(random_walk_similarity["end_link_id"])

            start_node = entity_node_map[start_link_id]
            end_node = entity_node_map[end_link_id]
            relation = Relationship(start_node, "connect", end_node)
            transaction.merge(relation)
            random_walk_similarity["relation"] = relation
            new_random_walk_similarity_list.append(random_walk_similarity)
        transaction.commit()
        for random_walk_similarity in new_random_walk_similarity_list:
            relation = random_walk_similarity["relation"]
            relation["count"] = random_walk_similarity["count"]
            graph.push(relation)
