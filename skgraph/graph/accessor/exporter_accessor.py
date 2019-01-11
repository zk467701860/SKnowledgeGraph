import traceback

from skgraph.graph.accessor.graph_accessor import GraphAccessor


class ExporterAccessor(GraphAccessor):
    def get_all_wikidata_node(self, limit=0):
        try:
            if limit <= 0:
                query = "MATCH (n:wikidata) return n"
            else:
                query = "MATCH (n:wikidata) return n limit " + str(limit)
            result = self.graph.run(query)
            node_list = []
            for record in result:
                node_list.append(record["n"])
            return node_list
        except Exception, error:
            traceback.print_exc()
            return []
