from db.engine_factory import EngineFactory
from db.model import ClassifiedWikipediaDocumentLR, WikidataAndWikipediaData, WikiDataProperty, WikidataAnnotation
from extractor.wikidata.WikiDataCreator import WikiDataNodeCreator
from extractor.wikidata.WikiDataItem import WikiDataItem
from shared.logger_util import Logger
from skgraph.graph.accessor.graph_client_for_wikidata import WikiDataGraphAccessor


class SoftwareRelatedWikidataConceptImporter:

    def __init__(self):
        self.logger_file_name = "import_wikidata_concept_to_neo4j"
        self.logger = None
        self.graphClient = None
        self.session = None

    def get_session(self):
        if not self.session:
            self.session = EngineFactory.create_session()
        return self.session

    def start_import_all_classify_result(self):
        session = self.get_session()

        MIN_SCORE = 0.5

        wikipedia_link_list = session.query(ClassifiedWikipediaDocumentLR).filter(
            ClassifiedWikipediaDocumentLR.score >= MIN_SCORE).all()
        for item in wikipedia_link_list:
            self.import_wikidata_entity(url=item.url)
        print("import classified result complete %d", len(wikipedia_link_list))

    def start_import_annotation_wikidata(self):
        session = self.get_session()

        wikidata_list = session.query(WikidataAnnotation).filter(
            WikidataAnnotation.type == 1).all()
        for item in wikidata_list:
            self.import_wikidata_entity(url=item.url)
        print("import annotation complete %d", len(wikidata_list))

    def init_importer(self, client=None):
        if client is None:
            return
        self.logger = Logger(self.logger_file_name).get_log()

        self.wikidata_accessor = WikiDataGraphAccessor(client)
        property_name_dict = {}
        session = EngineFactory.create_session()
        wikidata_property_list = session.query(WikiDataProperty.wd_item_id, WikiDataProperty.property_name).all()
        for wikipedia_property in wikidata_property_list:
            property_name_dict[wikipedia_property.wd_item_id] = wikipedia_property.property_name
        print("load all property name")
        self.wiki_creator = WikiDataNodeCreator(wikidata_graph_accessor=self.wikidata_accessor,
                                                init_property_from_file=False)
        self.wiki_creator.init_property_clean_Util(property_name_dict=property_name_dict)
        print("init wiki_creator")

    def import_wikidata_entity(self, url):
        if url is None or url == "":
            return
        session = self.get_session()

        wikipedia_wikidata_data = session.query(WikidataAndWikipediaData).filter(
            WikidataAndWikipediaData.wikipedia_url == url).first()
        if wikipedia_wikidata_data == None:
            self.import_wikipedia_entity(url=url)
            return
        if WikiDataItem.is_valid_json_string(wikipedia_wikidata_data.data_json) == False:
            self.import_wikipedia_entity(url=url)
            return

        wikidata_item = WikiDataItem(wd_item_id=None, init_at_once=False)
        wikidata_item = wikidata_item.init_wikidata_item_from_json_string(wikipedia_wikidata_data.data_json)

        if wikidata_item.is_init:
            self.wiki_creator.create_item_node_from_WikiDataItem_object(wikidata_item)

    def import_wikipedia_entity(self, url):
        if url is None or url == "":
            return
        self.wiki_creator.create_simple_wikipedia_node_from_wikipedia_url(url)
