import os

import pytest

from emush_rag.adapters.openai_embedder import OpenAIEmbedder
from emush_rag.config import Config


class TestOpenAIEmbedder:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")
        config = Config()
        self.embedder = OpenAIEmbedder(
            model=config.embedding_model,
            dimension=config.embedding_dimension,
            api_key=config.openrouter_api_key,
            base_url=config.llm_api_base_url,
        )

    def test_embed_returns_one_vector_of_the_embedder_dimension_per_text(self) -> None:
        embeddings = self.embedder.embed(["Myco-alarm", "NERON"])

        assert len(embeddings) == 2
        assert all(len(embedding) == self.embedder.dimension for embedding in embeddings)
