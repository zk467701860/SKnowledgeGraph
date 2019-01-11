from db.engine_factory import EngineFactory
from db.model import DocumentParagraphText
from fusion.entity_vector_computer import EntityVectorGenerator
from model_util.entity_vector.entity_vector_model import EntityVectorComputeModel

if __name__ == "__main__":
    generator = EntityVectorGenerator()
    generator.init(path="word2vec_api.txt", binary=True)
    generator.start_generate_paragraph_vector(output_path="mean_vector_api_paragraph.plain.txt")

