# Database

## Setup

- OpenSearch single node, security plugin disabled (reachable only from the Compose network and the server loopback), via `opensearch-py` in `adapters/opensearch_vector_store.py`.

## Main entities

- One kind of record: a document chunk with its metadata and its embedding.
- Versioned indices `emush_rag-<timestamp>` behind the alias `emush_rag`, which the API reads.

## Conventions

- Indexation writes a new index, then swaps the alias atomically: the API keeps serving the previous one until the new one is complete.
- The previous version is kept for rollback, older ones are deleted.
- No backup: the index is rebuilt from the wikis.
- Hybrid search: BM25 on `title^2` and `content` plus k-NN on `embedding`, min-max normalised, weighted by `hybrid_search_keyword_weight` (keywords 0.3).
- Chunk ids are derived from content, so identical chunks deduplicate.
- The OpenSearch image is pinned in `compose.yml`, `compose.prod.yml` and `tests/conftest.py`: bump all three together.
