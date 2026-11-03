from abc import ABC, abstractmethod


class Embedder(ABC):
    """Embedder interface. It turns texts into vectors, so the vector store can compare them by meaning."""

    dimension: int

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        pass
