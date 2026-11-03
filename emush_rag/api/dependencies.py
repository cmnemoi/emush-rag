from datetime import datetime

from chromadb import HttpClient
from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction

from emush_rag.adapters.chroma_vector_store import ChromaVectorStore
from emush_rag.adapters.in_memory_rate_limiter import InMemoryRateLimiter
from emush_rag.adapters.openai_llm_client import OpenAILLMClient
from emush_rag.config import Config
from emush_rag.ports.rate_limiter import RateLimiter
from emush_rag.usecases.answer_user_question import AnswerUserQuestion

config = Config()


def answer_user_question() -> AnswerUserQuestion:
    return AnswerUserQuestion(llm_client=_llm_client(), vector_store=_vector_store(_embedding_function()))


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


def _vector_store(embedding_function: OpenAIEmbeddingFunction) -> ChromaVectorStore:
    return ChromaVectorStore(
        client=HttpClient(
            host=config.vector_store_url,
            port=config.vector_store_port,
        ),
        collection_name=config.collection_name,
        embedding_function=embedding_function,
    )


def _embedding_function() -> OpenAIEmbeddingFunction:
    return OpenAIEmbeddingFunction(
        api_key=config.openrouter_api_key, model_name=config.embedding_model, api_base=config.llm_api_base_url
    )
