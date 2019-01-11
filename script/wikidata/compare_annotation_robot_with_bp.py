from db.engine_factory import EngineFactory
from db.model import ClassifiedWikipediaDocumentLR

if __name__ == "__main__":
    session = EngineFactory.create_session()
    #TODO
    ClassifiedWikipediaDocumentLR.
