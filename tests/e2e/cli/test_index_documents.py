import json
import shutil
import tempfile
from pathlib import Path

import pytest
from opensearchpy import OpenSearch
from typer.testing import CliRunner, Result

from emush_rag.adapters.opensearch_vector_store import OpenSearchVectorStore
from emush_rag.cli.index_documents import create_app
from tests.conftest import OpenSearchAddress
from tests.test_doubles import FakeEmbedder


class TestIndexDocumentsCLI:
    @pytest.fixture(autouse=True)
    def setup(self, opensearch_address: OpenSearchAddress, opensearch_client: OpenSearch) -> None:
        self.opensearch_address = opensearch_address
        self.sample_documents = self._create_sample_documents()
        self.temp_dir = self._create_temp_dir()
        self.data_dir = self._create_data_dir()
        self._write_sample_documents_to_file()

    def teardown_method(self) -> None:
        self._cleanup_temp_directories()

    def test_should_index_json_files_from_data_folder(self) -> None:
        # Given a CLI runner
        runner = self._create_cli_runner()

        # When indexing documents using the CLI
        result = self._run_index_documents_command(runner, index_alias="my_alias")

        # Then the command should succeed
        self._assert_command_succeeded(result)

        # And documents should be served under the alias
        indexed_documents = self._get_indexed_documents(index_alias="my_alias")
        self._assert_documents_were_indexed_correctly(indexed_documents)

    def test_reindexing_replaces_the_documents_served_under_the_alias(self) -> None:
        # Given documents already indexed
        runner = self._create_cli_runner()
        self._run_index_documents_command(runner, index_alias="my_alias")

        # When indexing again after one document was removed
        self.sample_documents = self.sample_documents[:1]
        self._write_sample_documents_to_file()
        result = self._run_index_documents_command(runner, index_alias="my_alias")

        # Then only the remaining document should be served
        self._assert_command_succeeded(result, nb_documents=1)
        indexed_documents = self._get_indexed_documents(index_alias="my_alias")
        self._assert_documents_were_indexed_correctly(indexed_documents)

    def _create_sample_documents(self) -> list[dict]:
        return [
            {
                "title": "Test 1",
                "content": "This is test document 1",
                "link": "http://example.com/1",
                "source": "test",
            },
            {
                "title": "Test 2",
                "content": "This is test document 2",
                "link": "http://example.com/2",
                "source": "test",
            },
        ]

    def _create_temp_dir(self) -> str:
        return tempfile.mkdtemp()

    def _create_data_dir(self) -> Path:
        data_dir = Path(self.temp_dir) / "data"
        data_dir.mkdir()
        return data_dir

    def _write_sample_documents_to_file(self) -> None:
        with open(self.data_dir / "documents.json", "w") as f:
            json.dump(self.sample_documents, f)

    def _cleanup_temp_directories(self) -> None:
        shutil.rmtree(self.temp_dir)

    def _create_cli_runner(self) -> CliRunner:
        return CliRunner()

    def _run_index_documents_command(self, runner: CliRunner, index_alias: str) -> Result:
        args = [
            "--data-dir",
            str(self.data_dir),
            "--vector-store-url",
            self.opensearch_address.host,
            "--vector-store-port",
            str(self.opensearch_address.port),
            "--index-alias",
            index_alias,
        ]
        return runner.invoke(create_app(embedder=FakeEmbedder()), args)

    def _assert_command_succeeded(self, result: Result, nb_documents: int = 2) -> None:
        assert result.exit_code == 0, result.output
        assert f"{nb_documents} documents indexed successfully" in result.stdout

    def _get_indexed_documents(self, index_alias: str) -> list:
        vector_store = OpenSearchVectorStore(
            host=self.opensearch_address.host,
            port=self.opensearch_address.port,
            alias=index_alias,
            embedder=FakeEmbedder(),
        )
        return vector_store.get_all_documents()

    def _assert_documents_were_indexed_correctly(self, indexed_documents: list) -> None:
        assert len(indexed_documents) == len(self.sample_documents)
        assert all(doc.metadata["title"] in [d["title"] for d in self.sample_documents] for doc in indexed_documents)
