from tqdm import tqdm

from emush_rag.models.document import Document
from emush_rag.ports.document_reader import DocumentReader
from emush_rag.ports.document_splitter import DocumentSplitter
from emush_rag.ports.vector_store import VectorStore


class IndexDocuments:
    """
    Use case to index documents in the vector store. It splits large documents into smaller chunks before indexing them.
    Chunks are indexed in a new version of the store, served only once complete.
    """

    def __init__(
        self,
        document_reader: DocumentReader,
        vector_store: VectorStore,
        document_splitter: DocumentSplitter,
        batch_size: int = 10,
    ):
        self.document_reader = document_reader
        self.vector_store = vector_store
        self.document_splitter = document_splitter
        self.batch_size = batch_size

    def execute(self) -> None:
        """
        Index documents in the vector store. Large documents are split into smaller chunks before indexing them.
        """
        documents = self.document_reader.read_documents()
        chunks = self._split_documents_into_chunks(documents)

        self.vector_store.start_new_version()
        for chunk_index in tqdm(
            range(0, len(chunks), self.batch_size),
            desc=f"Indexing documents in batches of {self.batch_size}...",
        ):
            self.vector_store.index_documents(chunks[chunk_index : chunk_index + self.batch_size])
        self.vector_store.publish_new_version()

    def _split_documents_into_chunks(self, documents: list[Document]) -> list[Document]:
        return list(set([chunk for document in documents for chunk in self.document_splitter.split(document)]))
