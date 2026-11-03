import typer

from emush_rag.adapters.file_system_json_document_reader import FileSystemJsonDocumentReader
from emush_rag.adapters.langchain_recursive_character_document_splitter import (
    LangchainRecursiveCharacterDocumentSplitter,
)
from emush_rag.adapters.openai_embedder import OpenAIEmbedder
from emush_rag.adapters.opensearch_vector_store import OpenSearchVectorStore
from emush_rag.config import Config
from emush_rag.ports.embedder import Embedder
from emush_rag.usecases.index_documents import IndexDocuments

config = Config()


def create_app(embedder: Embedder) -> typer.Typer:
    app = typer.Typer()

    @app.command()
    def main(
        batch_size: int = typer.Option(config.indexation_batch_size, help="Number of documents to index at once"),
        nb_characters_per_document: int = typer.Option(
            config.indexation_nb_characters_per_document, help="Number of characters per document"
        ),
        data_dir: str = typer.Option(config.data_directory, help="Path to directory containing documents to index"),
        vector_store_url: str = typer.Option(config.vector_store_url, help="OpenSearch host"),
        vector_store_port: int = typer.Option(config.vector_store_port, help="OpenSearch port"),
        index_alias: str = typer.Option(config.index_alias, help="Alias under which the API reads the documents"),
    ) -> None:
        """Index JSON documents from data directory into OpenSearch"""
        vector_store = OpenSearchVectorStore(
            host=vector_store_url,
            port=vector_store_port,
            alias=index_alias,
            embedder=embedder,
        )
        index_documents_usecase = IndexDocuments(
            document_reader=FileSystemJsonDocumentReader(data_directory=data_dir),
            vector_store=vector_store,
            document_splitter=LangchainRecursiveCharacterDocumentSplitter(
                chunk_size=nb_characters_per_document,
                chunk_overlap=config.indexation_chunk_overlap,
            ),
            batch_size=batch_size,
        )
        index_documents_usecase.execute()

        indexed_documents = vector_store.get_all_documents()
        typer.echo(f"{len(indexed_documents)} documents indexed successfully!")

    return app


app = create_app(
    embedder=OpenAIEmbedder(
        model=config.embedding_model,
        dimension=config.embedding_dimension,
        api_key=config.openrouter_api_key,
        base_url=config.llm_api_base_url,
    )
)

if __name__ == "__main__":
    app()
