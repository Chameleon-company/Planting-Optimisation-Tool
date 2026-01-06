FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv
ENV UV_LINK_MODE=copy

# Copy dependency files first (better caching)
COPY backend/pyproject.toml backend/uv.lock ./backend/

# Copy local editable packages referenced by uv.lock/pyproject (monorepo)
COPY datascience ./datascience
COPY gis ./gis
COPY frontend ./frontend
# If some of these folders don't exist, tell me and we’ll remove them.

# Install deps for backend (uv will resolve editable deps now)
WORKDIR /app/backend
RUN uv sync

# Copy backend source code (after deps install for caching)
COPY backend/ ./ 

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]


