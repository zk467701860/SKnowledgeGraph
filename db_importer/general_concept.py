import traceback

from db.engine_factory import EngineFactory
from db.model import WikipediaEntityName, WikipediaEntityNameToWikipediaMapping, WikipediaDocument
from shared.url_util import URLUtil
from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient


class WikiAliasDBImporter:
    def __init__(self):
        self.graphClient = None
        self.session = None

    def init(self):
        self.graphClient = DefaultGraphAccessor(GraphClient(server_number=4))
        self.session = EngineFactory.create_session()
        print("init complete")

    def clean_table(self):
        WikipediaEntityName.delete_all(self.session)
        WikipediaEntityNameToWikipediaMapping.delete_all(self.session)

        print("delete all exist table")

    def start_import_wiki_aliases_to_db(self):
        label = "wikipedia"
        wiki_nodes = self.graphClient.get_all_nodes_by_label(label)

        for node in wiki_nodes:
            node_id = self.graphClient.get_id_for_node(node)
            # print ('node_id: %r', node_id)
            # name, site_enwiki, labels_ = ''
            name_set = set([])
            if 'name' in dict(node):
                # print ("name: %r", node['name'])
                if isinstance(node['name'], list):
                    for each in node['name']:
                        name_set.add(each)
                else:
                    name_set.add(node['name'])
            if 'site:enwiki' in dict(node):
                # print ('site_enwiki: %s', node['site:enwiki'])
                if isinstance(node['site:enwiki'], list):
                    for each in node['site:enwiki']:
                        title = URLUtil.parse_url_to_title(each)
                        # print ('site_name: %r', title)
                        name_set.add(title)
                else:
                    title = URLUtil.parse_url_to_title(node["site:enwiki"])
                    # print ('site_name: %r', title)
                    name_set.add(title)
            if 'labels_en' in dict(node):
                # print( "labels_en: ", node['labels_en'])
                if isinstance(node['labels_en'], list):
                    for each in node['labels_en']:
                        name_set.add(each)
                else:
                    name_set.add(node['labels_en'])
            if 'aliases_en' in dict(node):
                # print("aliases_en: ", node['aliases_en'])
                for each in node['aliases_en']:
                    name_set.add(each)
            # print (name_set)
            for name in name_set:
                try:
                    wikipedia_entity_name = WikipediaEntityName(node_id, str(name))
                    wikipedia_entity_name.find_or_create(self.session, autocommit=True)
                except Exception:
                    traceback.print_exc()
            # self.session.commit()
        self.session.commit()

    def start_generate_wiki_entity_text_map(self):
        wikipedia_entity_name_data = WikipediaEntityName.get_all_wikipedia_names(self.session)
        kg_id_list = set([])
        for each in wikipedia_entity_name_data:
            if each is not None:
                kg_id_list.add(each.kg_id)
        # print kg_id_list
        for kg_id in kg_id_list:
            node = self.graphClient.find_node_by_id(kg_id)
            if node is not None:
                if "site:enwiki" in dict(node):
                    title = URLUtil.parse_url_to_title(node["site:enwiki"])
                    wikipedia_doc = WikipediaDocument.get_document_by_wikipedia_title(self.session, title)
                    if wikipedia_doc is not None:
                        wikipedia_id = wikipedia_doc.id
                        wiki_name_to_wikipedia_mapping = WikipediaEntityNameToWikipediaMapping(kg_id, wikipedia_id)
                        wiki_name_to_wikipedia_mapping.find_or_create(self.session, autocommit=False)
        self.session.commit()

    def start_import(self):
        self.init()
        self.clean_table()
        self.start_import_wiki_aliases_to_db()
        self.start_generate_wiki_entity_text_map()
