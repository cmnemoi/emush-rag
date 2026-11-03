import pytest
from opensearchpy import OpenSearch

from emush_rag.adapters.opensearch_vector_store import OpenSearchVectorStore
from emush_rag.models.document import Document, DocumentMetadata
from tests.conftest import OpenSearchAddress
from tests.test_doubles import FakeEmbedder


class TestOpenSearchVectorStore:
    @pytest.fixture(autouse=True)
    def setup(self, opensearch_address: OpenSearchAddress, opensearch_client: OpenSearch) -> None:
        self.client = opensearch_client
        self.store = OpenSearchVectorStore(
            host=opensearch_address.host, port=opensearch_address.port, alias="my_alias", embedder=FakeEmbedder()
        )
        self._given_a_published_empty_version()

    def test_indexed_documents_keep_their_content_and_metadata(self) -> None:
        document = self._given_a_document_with_metadata(
            content="test content",
            metadata=self._given_document_metadata(title="test title", link="test link", source="test source"),
        )

        self._when_indexing_documents([document])

        self._then_stored_documents_should_match([document])

    def test_indexing_the_same_document_twice_stores_it_once(self) -> None:
        document = self._given_sample_documents()[0]

        self._when_indexing_documents([document])
        self._when_indexing_documents([document])

        self._then_stored_documents_should_match([document])

    def test_get_relevant_documents_returns_at_most_the_requested_number_of_documents(self) -> None:
        documents = self._given_sample_documents()
        self._when_indexing_documents(documents)

        relevant_documents = self._when_getting_relevant_documents("test query", 2)

        self._then_documents_should_match_original(relevant_documents, documents)
        assert len(relevant_documents) == 2

    def test_get_relevant_documents_ranks_the_document_matching_the_query_first(self) -> None:
        mycoalarm = self._given_a_document_with_metadata(
            content="The Myco-alarm rings when a Mush extracts a spore",
            metadata=self._given_document_metadata(title="Myco-alarm", link="link 1", source="wiki"),
        )
        neron = self._given_a_document_with_metadata(
            content="NERON is the artificial intelligence of the Daedalus",
            metadata=self._given_document_metadata(title="NERON", link="link 2", source="wiki"),
        )
        self._when_indexing_documents([neron, mycoalarm])

        relevant_documents = self._when_getting_relevant_documents("Does the Myco-alarm detect spore extraction?", 2)

        assert relevant_documents[0] == mycoalarm

    def test_new_version_is_not_served_until_published(self) -> None:
        current_document, new_document = self._given_sample_documents()
        self._when_indexing_documents([current_document])

        self.store.start_new_version()
        self._when_indexing_documents([new_document])

        self._then_stored_documents_should_match([current_document])

    def test_published_version_replaces_the_served_documents(self) -> None:
        current_document, new_document = self._given_sample_documents()
        self._when_indexing_documents([current_document])
        self.store.start_new_version()
        self._when_indexing_documents([new_document])

        self.store.publish_new_version()

        self._then_stored_documents_should_match([new_document])

    def test_publishing_keeps_the_previous_version_for_rollback_and_deletes_older_ones(self) -> None:
        self._given_a_published_empty_version()
        previous_version = self.store.index_being_written
        self._given_a_published_empty_version()

        assert set(self.client.indices.get(index="my_alias-*")) == {previous_version, self.store.index_being_written}

    def _given_a_published_empty_version(self) -> None:
        self.store.start_new_version()
        self.store.publish_new_version()

    def _given_sample_documents(self) -> list[Document]:
        return [
            self._given_a_document_with_metadata(
                content=f"test content {i}",
                metadata=self._given_document_metadata(
                    title=f"test title {i}", link=f"test link {i}", source=f"test source {i}"
                ),
            )
            for i in range(1, 3)
        ]

    def _given_a_document_with_metadata(self, content: str, metadata: DocumentMetadata) -> Document:
        return Document(content=content, metadata=metadata)

    def _given_document_metadata(self, title: str, link: str, source: str) -> DocumentMetadata:
        return DocumentMetadata(title=title, link=link, source=source)

    def _when_indexing_documents(self, documents: list[Document]) -> None:
        self.store.index_documents(documents)

    def _when_getting_relevant_documents(self, query: str, max_relevant_documents: int) -> list[Document]:
        return self.store.get_relevant_documents(query, max_relevant_documents)

    def _then_stored_documents_should_match(self, expected_documents: list[Document]) -> None:
        assert self.store.get_all_documents() == expected_documents

    def _then_documents_should_match_original(
        self, actual_documents: list[Document], expected_documents: list[Document]
    ) -> None:
        assert all(doc in expected_documents for doc in actual_documents)
