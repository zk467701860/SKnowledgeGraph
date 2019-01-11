# !/usr/bin/python
# -*-coding:utf-8-*-
import sys

from db.engine_factory import EngineFactory
from db.model import WikipediaDocument, DocumentSentenceText, DomainEntity, APIEntity, APIHTMLText, \
    DocumentParagraphText, DocumentText
from model_util.entity_vector.entity_vector_model import EntityVectorComputeModel
from shared.url_util import URLUtil
from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient

reload(sys)

sys.setdefaultencoding('utf-8')


class EntityVectorGenerator:
    def __init__(self):
        self.session = None
        self.graphClient = None
        self.entity_vector_model = None

    def init(self, path="word2vec_api_software_wiki.txt", binary=True):
        self.session = EngineFactory.create_session()
        self.graphClient = DefaultGraphAccessor(GraphClient(server_number=4))

        self.entity_vector_model = EntityVectorComputeModel()
        self.entity_vector_model.init_word2vec_model(path=path, binary=binary)
        print("init complete")

    def get_content_for_wikidata_node(self, node):
        content = ""
        node_dict = dict(node)
        if 'site:enwiki' in node_dict:
            title = URLUtil.parse_url_to_title(node["site:enwiki"])
            wikipedia_doc = WikipediaDocument.get_document_by_wikipedia_title(self.session, title)
            if wikipedia_doc is not None:
                return wikipedia_doc.content
            else:
                content = content + " " + title

        property_list = ['labels_en', 'descriptions_en', 'aliases_en']
        for key in property_list:
            if key not in node_dict:
                continue
            if type(node[key]) == list:
                content = content + " " + " ".join(node[key])
            else:
                content = content + " " + node[key]

        if content is '':
            return None
        print("content: ", content)
        return content

    def start_generate_wikipedia_vector(self, output_path="wikipedia.plain.txt"):

        label = "wikipedia"

        wiki_nodes = self.graphClient.get_all_nodes_by_label(label)
        data_list = []
        for node in wiki_nodes:
            content = self.get_content_for_wikidata_node(node=node)
            if content is None:
                print("------None-----")
                continue
            item = {"id": "kg#" + str(self.graphClient.get_id_for_node(node)), "text": content}
            data_list.append(item)

        self.entity_vector_model.train_mean_vector_from_corpus(data_set=data_list,
                                                               output_path=output_path)

    def start_generate_sentence_vector(self, output_path="sentence.plain.txt"):
        session = self.session
        sentence_list = DocumentSentenceText.get_all_valid_sentences(session)
        data_list = []
        for each in sentence_list:
            if each.id is not None and each.text is not None:
                item = {"id": each.id, "text": each.text}
                data_list.append(item)
        self.entity_vector_model.train_mean_vector_from_corpus(data_set=data_list,
                                                               output_path=output_path)

    def start_generate_domain_entity_vector(self, output_path="domain_entity.plain.txt"):
        domain_entity_data = DomainEntity.get_all_domain_entities(self.session)

        data_list = []
        for each in domain_entity_data:
            if each.id is not None and each.description is not None:
                item = {"id": each.id, "text": each.name + " " + each.description}
                data_list.append(item)
        self.entity_vector_model.train_mean_vector_from_corpus(data_set=data_list,
                                                               output_path=output_path)

    def start_generate_api_entity_vector(self, output_path="api.plain.txt"):
        api_id_list = APIEntity.get_api_id_and_qualified_name_list(self.session)

        if api_id_list is not None:
            data_list = []
            for each in api_id_list:
                api_id = each.id
                api_name = each.qualified_name
                try:
                    api_name_simple_name = api_name.split("(")[0].split(".")[-1]
                except:
                    api_name_simple_name = ""

                # api_clean_text_data = APIHTMLText.get_text_by_api_id_and_type(self.session, api_id,
                #                                                               APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)

                api_html_text = APIHTMLText.get_html_text_id(self.session, api_id,
                                                             APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
                if api_html_text is None:
                    continue
                document_text = DocumentText.get_by_html_text_id(self.session, api_html_text.id)
                if document_text is None:
                    continue

                paragraph_text = DocumentParagraphText.get_first_by_doc_id(self.session, document_text.id)
                if paragraph_text is None:
                    continue
                if paragraph_text is not None:
                    api_clean_text = paragraph_text.text
                    final_text = api_name_simple_name + " " + api_name + " " + api_clean_text
                    item = {"id": api_id, "text": final_text}
                    data_list.append(item)
            self.entity_vector_model.train_mean_vector_from_corpus(data_set=data_list,
                                                                   output_path=output_path)

    def start_generate_paragraph_vector(self, output_path="mean_vector_api_paragraph.plain.txt"):
        paragraph_list = DocumentParagraphText.get_all_paragraph_text(session=self.session)
        text_data_set = []

        for paragraph in paragraph_list:
            text = paragraph.text
            if text is None or len(text.strip()) <= 2:
                continue
            text = text.strip()
            item = {"id": paragraph.id, "text": text}
            text_data_set.append(item)

        self.entity_vector_model.train_mean_vector_from_corpus(data_set=text_data_set,
                                                               output_path=output_path)
