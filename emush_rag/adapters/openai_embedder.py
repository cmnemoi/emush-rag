from openai import OpenAI

from emush_rag.ports.embedder import Embedder


class OpenAIEmbedder(Embedder):
    def __init__(self, model: str, dimension: int, api_key: str | None, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts, dimensions=self.dimension)
        return [embedding.embedding for embedding in sorted(response.data, key=lambda embedding: embedding.index)]
