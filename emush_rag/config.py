import os
from dataclasses import dataclass


@dataclass
class Config:
    chat_model: str = "openai/gpt-5.6-luna"
    data_directory: str = "data"
    embedding_model: str = "openai/text-embedding-3-large"
    embedding_dimension: int = 3072
    evaluation_model: str = "openai/gpt-4o-mini"
    rate_limit_max_requests: int = 100
    rate_limit_window_seconds: int = 60
    indexation_batch_size: int = 100
    indexation_nb_characters_per_document: int = 1_000
    indexation_chunk_overlap: int = 100
    max_relevant_documents: int = 5
    hybrid_search_keyword_weight: float = 0.3
    index_alias: str = "emush_rag"
    llm_api_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    vector_store_url: str = os.getenv("VECTOR_STORE_URL", default="vector_store")
    vector_store_port: int = int(os.getenv("VECTOR_STORE_PORT", default=9200))
