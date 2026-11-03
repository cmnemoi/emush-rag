import random
import string

import pytest

from emush_rag.adapters.langchain_recursive_character_document_splitter import (
    LangchainRecursiveCharacterDocumentSplitter,
)
from emush_rag.models.document import Document, DocumentMetadata
from emush_rag.usecases.index_documents import IndexDocuments
from tests.test_doubles import FakeVectorStore
from tests.test_doubles.test_doubles import InMemoryJsonDocumentReader


class TestIndexDocuments:
    def setup_method(self):
        self.document_reader = InMemoryJsonDocumentReader()
        self.vector_store = FakeVectorStore()
        self.chunk_size = 100
        self.batch_size = 10
        self.index_documents = IndexDocuments(
            document_reader=self.document_reader,
            vector_store=self.vector_store,
            document_splitter=LangchainRecursiveCharacterDocumentSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=0,
            ),
            batch_size=self.batch_size,
        )

    def test_should_index_small_documents_without_splitting_them(self):
        documents = self._create_documents_with_content(2, content="small content")

        self.index_documents.execute()

        self._assert_documents_indexed(documents)
        self._assert_batch_count(1)

    def test_should_index_documents_in_batches_when_more_than_batch_size(self):
        self._create_documents_with_content(11, content="small content")

        self.index_documents.execute()

        self._assert_batch_count(2)

    def test_should_split_large_document_and_index_chunks_in_batches(self):
        large_content = random.choice(string.ascii_letters) * 250  # Will be split into 3 chunks of ~83 characters each
        self._create_documents_with_content(1, content=large_content)

        self.index_documents.execute()

        self._assert_batch_count(1)  # 3 chunks fit in one batch of 10

    def test_should_split_multiple_large_documents_and_batch_all_chunks(self):
        # Create unique content for each document to ensure unique chunks
        documents = []
        for i in range(4):
            # Each document gets unique content that will produce 3 unique chunks
            unique_content = f"document{i}_" + "content" * 35  # ~250 chars with unique prefix
            doc = self._create_document_with_metadata(content=unique_content, title_suffix=f"-{i + 1}")
            documents.append(doc)

        self.document_reader.set_json_entries(documents)  # 4 docs * 3 chunks = 12 unique chunks

        self.index_documents.execute()

        self._assert_batch_count(2)  # 12 chunks need 2 batches of 10

    def test_should_handle_empty_document_list(self):
        self._create_documents_with_content(0)

        self.index_documents.execute()

        self._assert_batch_count(0)

    def test_should_preserve_document_metadata_in_chunks(self):
        original_document = self._create_document_with_metadata(
            content=random.choice(string.ascii_letters) * 250,  # Will be split into chunks
            title="Test Title",
            link="https://example.com",
            source="test_source",
        )
        self.document_reader.set_json_entries([original_document])

        self.index_documents.execute()

        indexed_documents = self.vector_store.get_all()
        assert len(indexed_documents) > 1  # Document was split
        for chunk in indexed_documents:
            assert chunk.metadata["title"] == "Test Title"
            assert chunk.metadata["link"] == "https://example.com"
            assert chunk.metadata["source"] == "test_source"

    def test_reindexing_serves_only_the_new_documents(self):
        self._create_documents_with_content(2, content="old content")
        self.index_documents.execute()
        new_documents = self._create_documents_with_content(1, content="new content")

        self.index_documents.execute()

        self._assert_documents_indexed(new_documents)

    def test_failed_reindexing_keeps_serving_the_current_documents(self):
        current_documents = self._create_documents_with_content(2, content="current content")
        self.index_documents.execute()
        self.vector_store.fails_on_batch = self.vector_store.nb_calls + 1
        self._create_documents_with_content(1, content="new content")

        with pytest.raises(ConnectionError):
            self.index_documents.execute()

        self._assert_documents_indexed(current_documents)

    def _create_documents_with_content(self, count: int, content: str = "default content") -> list[Document]:
        documents = [
            self._create_document_with_metadata(content=content, title_suffix=f"-{i}") for i in range(1, count + 1)
        ]
        self.document_reader.set_json_entries(documents)
        return documents

    def _create_document_with_metadata(
        self,
        content: str = "default content",
        title_suffix: str = "",
        title: str = "title",
        link: str = "https://example.com",
        source: str = "source",
    ) -> Document:
        return Document(
            content=content,
            metadata=DocumentMetadata(
                title=f"{title}{title_suffix}",
                link=f"{link}{title_suffix}",
                source=f"{source}{title_suffix}",
            ),
        )

    def _assert_documents_indexed(self, expected_documents: list[Document]):
        indexed_documents = self.vector_store.get_all()
        assert len(indexed_documents) == len(expected_documents)
        for expected_doc in expected_documents:
            assert any(
                doc.content == expected_doc.content and doc.metadata == expected_doc.metadata
                for doc in indexed_documents
            )

    def _assert_batch_count(self, expected_batch_count: int):
        self.vector_store.should_be_called_times(expected_batch_count)
