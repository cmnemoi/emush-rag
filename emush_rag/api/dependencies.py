from datetime import datetime

from opensearchpy import OpenSearch

from emush_rag.adapters.in_memory_rate_limiter import InMemoryRateLimiter
from emush_rag.adapters.openai_embedder import OpenAIEmbedder
from emush_rag.adapters.openai_llm_client import OpenAILLMClient
from emush_rag.adapters.opensearch_vector_store import OpenSearchVectorStore
from emush_rag.config import Config
from emush_rag.ports.rate_limiter import RateLimiter
from emush_rag.usecases.answer_user_question import AnswerUserQuestion

config = Config()


def answer_user_question() -> AnswerUserQuestion:
    return AnswerUserQuestion(llm_client=_llm_client(), vector_store=_vector_store())


def rate_limiter(datetime_provider: type[datetime] = datetime) -> RateLimiter:  # type: ignore[assignment]
    return InMemoryRateLimiter(
        max_requests=config.rate_limit_max_requests,
        window_seconds=config.rate_limit_window_seconds,
        datetime_provider=datetime_provider,
    )


def _llm_client() -> OpenAILLMClient:
    return OpenAILLMClient(
        model=config.chat_model, api_key=config.openrouter_api_key, base_url=config.llm_api_base_url
    )


def _vector_store() -> OpenSearchVectorStore:
    return OpenSearchVectorStore(
        client=OpenSearch(hosts=[{"host": config.vector_store_url, "port": config.vector_store_port}]),
        alias=config.index_alias,
        embedder=embedder(),
    )


def embedder() -> OpenAIEmbedder:
    return OpenAIEmbedder(
        model=config.embedding_model,
        dimension=config.embedding_dimension,
        api_key=config.openrouter_api_key,
        base_url=config.llm_api_base_url,
    )
