from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient


class GraphIndexInit:
    def __init__(self, graph_client=None):
        self.graph_client = graph_client

    def init_graph_index(self):
        if self.graph_client is None:
            print("graphClient is None")
            return
        accessor = DefaultGraphAccessor(graph=self.graph_client)
        accessor.create_index("CREATE INDEX ON :`api`(`api_id`)")
        accessor.create_index("CREATE INDEX ON :`entity`(`api_id`)")
        accessor.create_index("CREATE INDEX ON :`wikidata`(`wd_item_id`)")
        accessor.create_index("CREATE INDEX ON :`entity`(`wd_item_id`)")
        accessor.create_index("CREATE INDEX ON :`entity`(`site:enwiki`)")
        accessor.create_index("CREATE INDEX ON :`wikipedia`(`site:enwiki`)")
        accessor.create_index("CREATE INDEX ON :`wikidata`(`site:enwiki`)")
        accessor.create_index("CREATE INDEX ON :`entity`(`sentence_id`)")
        accessor.create_index("CREATE INDEX ON :`sentence`(`sentence_id`)")

        accessor.create_index("CREATE INDEX ON :`entity`(`domain_entity_id`)")
        accessor.create_index("CREATE INDEX ON :`domain entity`(`domain_entity_id`)")
