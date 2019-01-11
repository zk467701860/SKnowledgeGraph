import json

from db.engine_factory import EngineFactory
from db.model import DocumentSentenceText

if __name__ == "__main__":
    session = EngineFactory.create_session()
    sentence_jsons = []
    filename = "all_sentence_list.json"
    with open(filename, 'w') as f:
        sentence_list = DocumentSentenceText.get_all_valid_sentences(session=session)
        for sentence_entity in sentence_list:
            sentence_jsons.append({"sentence_id": sentence_entity.id, "text": sentence_entity.text})
        json.dump(sentence_jsons, f)
