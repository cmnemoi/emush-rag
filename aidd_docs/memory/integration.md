# Integration

## External services

- OpenRouter: chat completion (`adapters/openai_llm_client.py`) and embeddings (`adapters/openai_embedder.py`), through the OpenAI SDK with `base_url` set to OpenRouter.
- Models are named OpenRouter-style (`openai/...`) in `Config`; changing the embedding model or dimension requires a full reindexation.
- eMush wikis: scraped by `mush-wikis-scraper`, only during indexation (see `cli.md`).

## Calling conventions

- Auth: `OPENROUTER_API_KEY`, from `.env` locally (decrypted from `secrets.env`), from GitHub secrets in CI and production.
- No retry or timeout of our own: SDK defaults; a failed call surfaces as a 500.
- OpenAI calls are traced by the OpenTelemetry OpenAI instrumentation.
