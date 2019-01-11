import codecs
import json

from db.engine_factory import EngineFactory
from db.model import ClassifiedWikipediaDocumentLR
from shared.url_util import URLUtil


class WikiClassificationResultDBImporter:
    def __init__(self):
        pass

    def import_lr_wiki_classification_result(self, result_json_file_name):

        session = EngineFactory.create_session()
        prediction_list = []
        # file_path = os.path.split(os.path.realpath(__file__))[0] + "/" + result_json_file_name
        # with codecs.open(file_path, 'r', encoding='utf8') as f:

        ClassifiedWikipediaDocumentLR.delete_all(session)
        print("delete old classification result complete")
        with codecs.open(result_json_file_name, 'r', encoding='utf8') as f:
            prediction_list = json.load(f)
        print("load json complete")

        commit_step = 10000
        count = 0
        for prediction in prediction_list:
            score = prediction["score"]
            url = prediction["url"]
            title = URLUtil.parse_url_to_title(url)
            doc_id = prediction["doc_id"]
            if score > 0.5:
                type = ClassifiedWikipediaDocumentLR.TYPE_SOFTWARE_RELATED
            else:
                type = ClassifiedWikipediaDocumentLR.TYPE_SOFTWARE_UNRELATED
            classified_doc = ClassifiedWikipediaDocumentLR(title=title, url=url,
                                                           type=type, score=score, wikipedia_doc_id=doc_id)
            classified_doc.find_or_create(session=session, autocommit=False)
            count = count + 1
            if count > commit_step:
                count = 0
                session.commit()
        session.commit()
