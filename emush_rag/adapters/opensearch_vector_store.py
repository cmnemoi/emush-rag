from datetime import datetime
from typing import cast

from opensearchpy import OpenSearch, helpers

from emush_rag.config import Config
from emush_rag.models.document import Document, DocumentMetadata
from emush_rag.ports.embedder import Embedder
from emush_rag.ports.vector_store import VectorStore

config = Config()


class OpenSearchVectorStore(VectorStore):
    """
    Vector store backed by OpenSearch. Relevant documents are found with an hybrid search:
    keywords (BM25) catch exact game terms, embeddings (k-NN) catch the meaning of the question.

    Each version of the store is an index named after the alias, which serves the published version.
    """

    def __init__(
        self,
        client: OpenSearch,
        alias: str,
        embedder: Embedder,
        keyword_weight: float = config.hybrid_search_keyword_weight,
    ):
        self.client = client
        self.alias = alias
        self.embedder = embedder
        self.keyword_weight = keyword_weight
        self.index_being_written = alias

    def start_new_version(self) -> None:
        self.index_being_written = f"{self.alias}-{datetime.now():%Y%m%d%H%M%S%f}"
        self.client.indices.create(
            index=self.index_being_written,
            body={
                "settings": {"index": {"knn": True, "number_of_shards": 1, "number_of_replicas": 0}},
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "title": {"type": "text"},
                        "link": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": self.embedder.dimension,
                            "method": {"name": "hnsw", "engine": "lucene", "space_type": "cosinesimil"},
                        },
                    }
                },
            },
        )

    def index_documents(self, documents: list[Document]) -> None:
        if not documents:
            return

        embeddings = self.embedder.embed([document.content for document in documents])
        helpers.bulk(
            self.client,
            (
                {
                    "_index": self.index_being_written,
                    "_id": document.generate_id(),
                    "content": document.content,
                    **document.metadata,
                    "embedding": embedding,
                }
                for document, embedding in zip(documents, embeddings, strict=True)
            ),
            refresh="wait_for",
        )

    def get_relevant_documents(self, query: str, max_relevant_documents: int) -> list[Document]:
        [query_embedding] = self.embedder.embed([query])
        response = self.client.search(
            index=self.alias,
            body={
                "size": max_relevant_documents,
                "_source": {"excludes": ["embedding"]},
                "query": {
                    "hybrid": {
                        "queries": [
                            {"multi_match": {"query": query, "fields": ["title^2", "content"]}},
                            {"knn": {"embedding": {"vector": query_embedding, "k": max_relevant_documents}}},
                        ]
                    }
                },
                "search_pipeline": self._hybrid_search_pipeline(),
            },
        )
        return [self._to_document(hit["_source"]) for hit in response["hits"]["hits"]]

    def get_all_documents(self) -> list[Document]:
        return [
            self._to_document(hit["_source"])
            for hit in helpers.scan(self.client, index=self.alias, _source_excludes=["embedding"])
        ]

    def publish_new_version(self) -> None:
        """
        Atomically serve the new version under the alias. The previous version is kept for rollback,
        older ones are deleted.
        """
        previous_versions = self._published_versions()
        self.client.indices.update_aliases(
            body={
                "actions": [{"remove": {"index": index, "alias": self.alias}} for index in previous_versions]
                + [{"add": {"index": self.index_being_written, "alias": self.alias}}]
            }
        )
        self._delete_versions(keeping=previous_versions | {self.index_being_written})

    def _published_versions(self) -> set[str]:
        if not self.client.indices.exists_alias(name=self.alias):
            return set()
        return set(self.client.indices.get_alias(name=self.alias))

    def _delete_versions(self, keeping: set[str]) -> None:
        obsolete_versions = set(self.client.indices.get(index=f"{self.alias}-*")) - keeping
        for index in obsolete_versions:
            self.client.indices.delete(index=index)

    def _hybrid_search_pipeline(self) -> dict:
        return {
            "phase_results_processors": [
                {
                    "normalization-processor": {
                        "normalization": {"technique": "min_max"},
                        "combination": {
                            "technique": "arithmetic_mean",
                            "parameters": {"weights": [self.keyword_weight, 1 - self.keyword_weight]},
                        },
                    }
                }
            ]
        }

    def _to_document(self, source: dict) -> Document:
        return Document(
            content=source["content"],
            metadata=cast(DocumentMetadata, {key: source[key] for key in ("title", "link", "source")}),
        )
