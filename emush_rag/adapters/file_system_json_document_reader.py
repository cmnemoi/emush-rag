import json
from pathlib import Path

from emush_rag.models.document import Document
from emush_rag.ports.document_reader import DocumentReader


class FileSystemJsonDocumentReader(DocumentReader):
    """Implementation of DocumentReader that reads JSON files from the file system"""

    def __init__(self, data_directory: str):
        self.data_directory = data_directory

    def read_documents(self) -> list[Document]:
        """Read JSON files from data directory and return their contents as a list of Documents"""
        json_entries = []

        for file_path in Path(self.data_directory).glob("*.json"):
            with open(file_path, "r") as f:
                file_entries = json.load(f)
                # The scraper writes a null content for the pages it could not parse.
                json_entries.extend([Document.from_dict(entry) for entry in file_entries if entry["content"]])

        return json_entries
