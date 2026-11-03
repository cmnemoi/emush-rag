from dataclasses import dataclass
from typing import Iterator

import pytest
from opensearchpy import OpenSearch
from testcontainers.community.opensearch import OpenSearchContainer

OPENSEARCH_IMAGE = "opensearchproject/opensearch:3.8.0"


@pytest.fixture(scope="session")
def opensearch_container() -> Iterator[OpenSearchContainer]:
    with OpenSearchContainer(OPENSEARCH_IMAGE).with_env("OPENSEARCH_JAVA_OPTS", "-Xms512m -Xmx512m") as container:
        yield container


@dataclass(frozen=True)
class OpenSearchAddress:
    host: str
    port: int


@pytest.fixture
def opensearch_address(opensearch_container: OpenSearchContainer) -> OpenSearchAddress:
    config = opensearch_container.get_config()
    return OpenSearchAddress(host=config["host"], port=int(config["port"]))


@pytest.fixture
def opensearch_client(opensearch_container: OpenSearchContainer) -> Iterator[OpenSearch]:
    client = opensearch_container.get_client()
    yield client
    client.indices.delete(index="*")
