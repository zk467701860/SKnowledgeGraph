from tagme import wiki_title

from factory import NodeBuilder
from graph_accessor import GraphAccessor, DefaultGraphAccessor
from shared.logger_util import Logger

_logger = Logger("WikipediaGraphAccessor").get_log()


class WikipediaGraphAccessor(GraphAccessor):
    def create_wikipedia_item_entity_by_url(self, url):
        if url.startswith("https://en.wikipedia.org/") == False:
            return None
        accessor = DefaultGraphAccessor(self)
        node = accessor.get_node_by_wikipedia_link(url)
        if node is None:
            property_dict = {"name": wiki_title(url.split("/")[-1]), "url": url, "site:enwiki": url}
            if "(" in property_dict["name"]:
                alias = [(property_dict["name"].split(" ("))[0]]
                property_dict["alias"] = alias
            node = NodeBuilder().add_entity_label().add_label("wikipedia").add_property(**property_dict).build()
            self.graph.merge(node)
            _logger.info("create wikipedia node" + str(property_dict))
        return node
