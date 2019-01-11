# coding=utf-8
from entity_extractor.extract_pipeline import CandidateEntityExtractionPipeline

if __name__ == "__main__":
    pipeline = CandidateEntityExtractionPipeline()
    pipeline.start_extract_candidate_concept_entity_pipeline()
