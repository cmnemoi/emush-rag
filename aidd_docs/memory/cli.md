# CLI

## Commands

- `index-documents`: reads JSON documents from a directory, splits, embeds and loads them into a new OpenSearch index version, then publishes it.

## Interface

- Options default to `Config`: `--data-dir`, `--vector-store-url`, `--vector-store-port`, `--batch-size`, `--nb-characters-per-document`, `--index-alias`.
- Input: JSON arrays of `{title, link, source, content}`.

## Distribution

- Not published: run from the repo with `uv run emush_rag/cli/index_documents.py`.
- `make index-local-documents`: indexes `data/` into the local Compose OpenSearch.
- `make index-documents` / `scripts/index-production-documents`: scrapes the wikis to a temp dir, opens an SSH tunnel to the production OpenSearch (server loopback port `8162`), then indexes. Needs a `cmnemoi.production` SSH host.
- The same script runs every Monday at 6:00 from the `Index documents` workflow, or on demand.
