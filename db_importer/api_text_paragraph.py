import json

from db.engine_factory import EngineFactory
from db.model import APIHTMLText, DocumentText, DocumentSentenceText, DocumentParagraphText, SentenceToParagraphRelation


class ParagraphSplitterForDocument:
    def __init__(self):
        self.session = None

    def init(self):
        self.session = EngineFactory.create_session()

    def process_pre_tag(self, text):
        pre_map = {}
        if text is not None:
            index = 0
            while "<pre>" in text:
                pre_index = text.find("<pre>")
                suf_index = text.find("</pre>")
                pre_tag_text = text[pre_index: suf_index + 6]
                key = "@@pre" + str(index)
                text = text.replace(pre_tag_text, "\n\n" + key + "\n\n")
                pre_map.setdefault(key, pre_tag_text)
                index += 1
        return pre_map, text

    def split_paragraph(self, text, pre_map):
        result = []
        if text is not None:
            temp = text.split("\n\n")
            for each in temp:
                if each in pre_map.keys():
                    result.append(pre_map[each])
                else:
                    if "<p>" in each:
                        small_para = each.split("<p>")
                        for small in small_para:
                            result.append(small)
                    else:
                        result.append(each)
        return result

    def get_paragraph_index(self, sentence, paragraph_list):
        if sentence is not None and paragraph_list is not None:
            result_map = {}
            for i in range(0, len(paragraph_list)):
                result_map.setdefault(i, 0)
            word_list = sentence.split(" ")
            for word in word_list:
                word = word.replace(",", "").replace(";", "")
                for paragraph in paragraph_list:
                    if word in paragraph:
                        result_map[paragraph_list.index(paragraph)] += 1
            # print(sorted(result_map,key=lambda x:result_map[x])[-1])
            return sorted(result_map, key=lambda x: result_map[x])[-1]

    def key_value_shuffle(self, origin, value_domain):
        # print value_domain
        result = {}
        for value in range(0, value_domain):
            result.setdefault(value, [])
        for key in origin.keys():
            # print str(key), " ", str(origin[key])
            result[origin[key]].append(key)
        for key in result.keys():
            result[key] = sorted(result[key])
        return result

    def get_text_by_id(self, doc_sentence_data, sentence_id):
        for each in doc_sentence_data:
            if each.id == sentence_id:
                return each.text
        return None

    def start_split_paragraph(self, output_file="paragraph_data.txt"):

        session = self.session

        html_text_list = session.query(APIHTMLText).filter_by(
            html_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION).all()

        with open(output_file, 'w') as f:
            for html_text in html_text_list:

                html_id = html_text.id
                document_text = session.query(DocumentText.id).filter_by(html_text_id=html_id).first()
                if document_text is None:
                    continue

                doc_id = document_text.id
                doc_sentence_data = session.query(DocumentSentenceText).filter_by(doc_id=doc_id).all()

                pre_map, html = self.process_pre_tag(html_text.html)
                result = self.split_paragraph(html, pre_map)

                sentence_to_paragraph = {}
                num_set = []
                for each in doc_sentence_data:
                    sentence = each.text
                    paragraph_index = self.get_paragraph_index(sentence, result)
                    sentence_to_paragraph.setdefault(each.id, paragraph_index)
                    if paragraph_index not in num_set:
                        num_set.append(paragraph_index)

                for key in sentence_to_paragraph:
                    sentence_to_paragraph[key] = num_set.index(sentence_to_paragraph[key])

                paragraphs = self.key_value_shuffle(sentence_to_paragraph, len(num_set))

                doc_paragraph = []
                for key in paragraphs.keys():
                    sentence_list = paragraphs[key]
                    paragraph_text = ""
                    for sentence_id in sentence_list:
                        temp = self.get_text_by_id(doc_sentence_data, sentence_id)
                        if temp is not None:
                            paragraph_text += (temp + " ")
                    paragraph_data = {"doc_id": doc_id, "paragraph_index": key, "text": paragraph_text,
                                      "sentence_id_list": sentence_list}
                    doc_paragraph.append(paragraph_data)
                f.write(json.dumps(doc_paragraph))
                f.write('\n')

    def import_paragraph_data_from_json_file(self, paragraph_json_file='paragraph_data.txt'):
        session = self.session

        with open(paragraph_json_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                paragraph_data = json.loads(line)
                if len(paragraph_data) > 0:
                    for paragraph in paragraph_data:
                        paragraph_index = paragraph["paragraph_index"]
                        doc_id = paragraph["doc_id"]
                        text = paragraph["text"]
                        # print("paragraph index: ", paragraph_index)
                        # print("doc id: ", doc_id)
                        # print("text: ", text)
                        document_paragraph_text = DocumentParagraphText(doc_id, paragraph_index, text)
                        document_paragraph_text.find_or_create(session, autocommit=False)
            session.commit()

    def import_sentence_to_paragraph_relation_from_json_file(self, paragraph_json_file='paragraph_data.txt'):
        session = self.session
        with open(paragraph_json_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                paragraph_data = json.loads(line)
                if len(paragraph_data) > 0:
                    for paragraph in paragraph_data:
                        doc_id = paragraph["doc_id"]
                        paragraph_index = paragraph["paragraph_index"]
                        paragraph_id = DocumentParagraphText.get_id_by_doc_id_and_paragraph_index(session, doc_id,
                                                                                                  paragraph_index)
                        sentence_id_list = paragraph["sentence_id_list"]
                        # print paragraph_id
                        if paragraph_id != -1 and sentence_id_list is not None and len(sentence_id_list) > 0:
                            for sentence_id in sentence_id_list:
                                sentence_to_paragraph_relation = SentenceToParagraphRelation(paragraph_id, sentence_id)
                                sentence_to_paragraph_relation.find_or_create(session, autocommit=False)
            session.commit()
