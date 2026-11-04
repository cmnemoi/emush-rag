# API

## Style

- REST on FastAPI, routes in `emush_rag/api/main.py`, under `/api`, unversioned.

## Resources

- `POST /api/questions`: a question and its chat history, returns the answer and the retrieved documents.
- `GET /api/version`: the package version.

## Contracts

- Pydantic models in `emush_rag/api/models.py`; the OpenAPI spec and Swagger UI are served at `/docs`.
- Errors use FastAPI's `{"detail": ...}`: 429 past the rate limit, 500 on any use case failure.
- Rate limit: 100 requests per 60 s per client IP, on `/api/questions` only.
- CORS allows the Netlify frontend and the Vite dev server (`localhost:5173`); adding a frontend origin means editing `main.py`.
