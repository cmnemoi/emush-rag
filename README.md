# Ask NERON API

[![Continuous Integration](https://github.com/cmnemoi/emush_rag/actions/workflows/continuous_integration.yaml/badge.svg)](https://github.com/cmnemoi/emush_rag/actions/workflows/continuous_integration.yaml)
[![Continuous Delivery](https://github.com/cmnemoi/emush_rag/actions/workflows/create_github_release.yaml/badge.svg)](https://github.com/cmnemoi/emush_rag/actions/workflows/create_github_release.yaml)
[![codecov](https://codecov.io/gh/cmnemoi/emush_rag/graph/badge.svg?token=FLAARH38AG)](https://codecov.io/gh/cmnemoi/emush_rag)

A RAG-based API to answer questions about [eMush](https://emush.eternaltwin.org/) using curated data.

Stack: 
- [FastAPI](https://fastapi.tiangolo.com/) for the API, [pytest](https://docs.pytest.org/en/stable/) for automated testing ;
- [OpenSearch](https://opensearch.org/) for the hybrid search (keywords and embeddings) allowing document retrieval ;
- [Github Actions](https://github.com/features/actions) and [Docker Swarm](https://docs.docker.com/engine/swarm/) for automated deployment via a CI/CD pipeline on a self-managed [Digital Ocean server](https://www.digitalocean.com/products/droplets/) : https://askneron.com/docs
- [OpenTelemetry](https://opentelemetry.io/) for tracing and metrics (exported with [Jaeger](https://www.jaegertracing.io/)) ;
- [Grafana](https://grafana.com/) for monitoring dashboards from OpenTelemetry signals.

# Contributing

## Prerequisites

- [curl](https://curl.se/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [make](https://www.gnu.org/software/make/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

- Run the following command: `curl -sSL https://raw.githubusercontent.com/cmnemoi/emush_rag/main/clone-and-install | bash`
- Add an [OpenRouter API key](https://openrouter.ai/settings/keys) to the `.env` file.

## Usage

You can now ask questions to the API by running the following command:

```bash
curl -X POST "http://askneron.localhost/api/questions" \
     -H "Content-Type: application/json" \
     -d '{
           "question": "Do mycoalarms detect spore extraction?",
           "chat_history": []
         }'
```

Or by accessing the API Swagger at http://askneron.localhost/docs.

## Indexing new documents

To improve the answer of the RAG model, you can index new documents in the vector database by putting them in the `data` directory and running the following command:

```bash
make index-local-documents
```

`make index-documents` scrapes the wikis again and indexes them in production through an SSH tunnel. Documents go to a new index, which is served once complete: the previous index is kept for rollback.

## Development

- Lint code with `make lint`.
- Run tests with `make test`.

# License

The source code of this repository is licensed under the [AGPL-3.0-or-later License](LICENSE).

# Screenshots

![API docs with OpenAPI UI](./screenshots/api.png)
![Grafana dashboard](./screenshots/dashboard.png)
![Trace detail on Grafana](./screenshots/trace.png)