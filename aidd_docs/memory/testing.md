# Testing

## Strategy

- `tests/unit`: use cases against handwritten fakes of the ports.
- `tests/integration`: each adapter against the real thing: OpenSearch in a testcontainer, OpenRouter over the network.
- `tests/e2e`: the FastAPI app through `TestClient` and the Typer CLI, with dependency overrides.

## Tools

- pytest, pytest-asyncio, pytest-cov; coverage uploaded to Codecov by CI.
- testcontainers for OpenSearch, with a session-scoped container (`tests/conftest.py`).

## Conventions

- Handwritten in-memory fakes over mocks, in `tests/test_doubles/`.
- Time is injected (`datetime_provider`) and faked with `FakeDateTime`.
- Given-When-Then structure; test names state the expected behaviour with "should".
- Integration tests call OpenRouter for real: they need `OPENROUTER_API_KEY` and cost credits.

## Run

- `make test`: everything, with coverage.
- `make test-fast`: unit and integration only.
