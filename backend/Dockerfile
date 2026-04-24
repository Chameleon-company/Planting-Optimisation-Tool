FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv --no-cache-dir

WORKDIR /app

# Copy backend manifests first for layer caching - uv sync only re-runs when
# pyproject.toml or uv.lock change.
COPY backend/pyproject.toml backend/uv.lock backend/

# gis and datascience are editable workspace members - their full source must
# be present before uv sync or the build fails (they use an src layout).
COPY gis/ gis/
COPY datascience/ datascience/

WORKDIR /app/backend
RUN uv sync --frozen

# Copy backend source code last (most frequently changing layer)
WORKDIR /app
COPY backend/ backend/

WORKDIR /app/backend

# PORT is injected by Render at runtime. Falls back to 8080 for local use.
CMD uv run uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}
