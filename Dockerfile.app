# Step 1: Build the application
FROM python:3.15-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.8.2 /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

# Step 2: Run the application
FROM python:3.15-slim

# The application runs unprivileged and cannot modify its own code, owned by root.
RUN useradd --system --uid 10001 --create-home app

# Copy the environment, but not the source code
COPY --from=builder /app/.venv /app/.venv

USER app

EXPOSE 8080

# Run the application
CMD ["/app/.venv/bin/uvicorn", "emush_rag.api.main:app", "--host", "0.0.0.0", "--port", "8080"]