import typer
from chromadb import PersistentClient
from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction

from emush_rag.adapters.chroma_vector_store import ChromaVectorStore
from emush_rag.adapters.file_system_json_document_reader import FileSystemJsonDocumentReader
from emush_rag.adapters.langchain_recursive_character_document_splitter import (
    LangchainRecursiveCharacterDocumentSplitter,
)
from emush_rag.config import Config
from emush_rag.usecases.index_documents import IndexDocuments

app = typer.Typer()
config = Config()


@app.command()
def main(
    batch_size: int = typer.Option(config.indexation_batch_size, help="Number of documents to index at once"),
    nb_characters_per_document: int = typer.Option(
        config.indexation_nb_characters_per_document, help="Number of characters per document"
    ),
    data_dir: str = typer.Option(config.data_directory, help="Path to directory containing documents to index"),
    chroma_persist_dir: str = config.chroma_db_directory,
    collection_name: str = config.collection_name,
) -> None:
    """Index JSON documents from data directorya into Chroma vector store"""
    document_reader = FileSystemJsonDocumentReader(data_directory=data_dir)
    vector_store = ChromaVectorStore(
        client=PersistentClient(path=chroma_persist_dir),
        collection_name=collection_name,
        embedding_function=OpenAIEmbeddingFunction(
            api_key=config.openrouter_api_key, model_name=config.embedding_model, api_base=config.llm_api_base_url
        ),
    )
    index_documents_usecase = IndexDocuments(
        document_reader=document_reader,
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


if __name__ == "__main__":
    app()
