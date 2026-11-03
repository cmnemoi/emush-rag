from abc import ABC, abstractmethod

from emush_rag.models.document import Document


class VectorStore(ABC):
    """Vector store interface. This is where we will store our documents for them being used by the RAG model."""

    @abstractmethod
    def start_new_version(self) -> None:
        """Send the next indexed documents to a new, empty version of the store, not served yet."""
        pass

    @abstractmethod
    def index_documents(self, documents: list[Document]) -> None:
        pass

    @abstractmethod
    def publish_new_version(self) -> None:
        """Serve the new version in place of the current one."""
        pass

    @abstractmethod
    def get_relevant_documents(self, query: str, max_relevant_documents: int) -> list[Document]:
        pass
