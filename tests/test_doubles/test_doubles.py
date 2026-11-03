import math
import zlib
from typing import List

from emush_rag.models.document import Document
from emush_rag.ports.document_reader import DocumentReader
from emush_rag.ports.embedder import Embedder
from emush_rag.ports.llm_client import ChatMessage, LLMClient
from emush_rag.ports.vector_store import VectorStore
from emush_rag.usecases.answer_user_question import AnswerUserQuestion


class FakeVectorStore(VectorStore):
    """
    Fake vector store for testing purposes. It returns predefined documents.
    """

    def __init__(self, documents_to_return: List[Document] | None = None, fails_on_batch: int | None = None):
        self.documents_to_return = documents_to_return or []
        self.published_documents: List[Document] = []
        self.new_version_documents: List[Document] = []
        self.fails_on_batch = fails_on_batch
        self.nb_calls = 0

    def get_all(self) -> List[Document]:
        return self.published_documents

    def start_new_version(self) -> None:
        self.new_version_documents = []

    def index_documents(self, documents: List[Document]) -> None:
        self.nb_calls += 1
        if self.nb_calls == self.fails_on_batch:
            raise ConnectionError("Vector store unreachable")
        self.new_version_documents.extend(documents)

    def publish_new_version(self) -> None:
        self.published_documents = self.new_version_documents

    def get_relevant_documents(self, query: str, max_relevant_documents: int) -> List[Document]:
        return self.documents_to_return[:max_relevant_documents]

    def should_be_called_times(self, times: int):
        assert self.nb_calls == times


class FakeEmbedder(Embedder):
    """
    Fake embedder for testing purposes. Texts sharing words get close vectors, without calling any API.
    """

    dimension = 16

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> List[float]:
        # The last component is constant, so that no vector is null: cosine similarity is undefined for those.
        vector = [0.0] * (self.dimension - 1) + [1.0]
        for word in text.lower().split():
            vector[zlib.crc32(word.encode()) % (self.dimension - 1)] += 1.0
        norm = math.sqrt(sum(component**2 for component in vector))
        return [component / norm for component in vector]


class FakeLLMClient(LLMClient):
    """
    Fake LLM client for testing purposes. It returns predefined responses.
    """

    def __init__(
        self, expected_response: str = "This is a fake response", expected_messages: List[ChatMessage] | None = None
    ):
        self.expected_response = expected_response
        self.expected_messages = expected_messages

    def complete(self, system_prompt: str, messages: List[ChatMessage]) -> str:
        if self.expected_messages is not None:
            assert messages == self.expected_messages
        return self.expected_response


class InMemoryJsonDocumentReader(DocumentReader):
    """
    Fake document reader for testing purposes. It returns predefined documents.
    """

    json_entries: List[Document]

    def read_documents(self) -> List[Document]:
        return self.json_entries

    def set_json_entries(self, json_entries: List[Document]) -> None:
        self.json_entries = json_entries


def fake_answer_user_question():
    vector_store = FakeVectorStore()
    llm_client = FakeLLMClient()

    return AnswerUserQuestion(llm_client=llm_client, vector_store=vector_store)
