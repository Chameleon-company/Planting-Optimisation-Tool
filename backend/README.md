# Not complete, just jotting notes

Activate virtual environment

```bash
source .venv/bin/activate
```

To run the fastapi server:

```bash
fastapi dev main.py
```

Navigate to `http://127.0.0.1:8000 # default` in browser

## Makefile

| Target | Purpose | Shell Commands Executed |
| :--- | :--- | :--- |
| **`setup`** | Initializes the database container from scratch (`db-teardown`), starts the service, and applies all pending Alembic migrations. | 1. `docker compose down -v` (via `db-teardown`) 2. `docker compose up -d db` (via `db-start`) 3. `sleep 5` 4. `uv run dotenv run alembic upgrade head` (via `db-migrate`) |
| **`db-teardown`** | Stops and removes the PostgreSQL container and all associated data volumes for a clean start. | `docker compose down -v` |
| **`db-start`** | Ensures a clean state (`db-teardown`) then starts the PostgreSQL container service in detached mode. | 1. `docker compose down -v` (via `db-teardown`) 2. `docker compose up -d db` 3. `sleep 5` |
| **`db-migrate`** | Applies any pending Alembic migration scripts to upgrade the database schema to the latest version. | `uv run dotenv run alembic upgrade head` |
| **`revision`** | Generates a new Alembic migration script based on changes detected in your Python models. **Requires `M="message"`**. | `uv run dotenv run alembic revision --autogenerate -m "message"` |
| **`test`** | Executes the full test suite using Pytest on the contents of the `tests/` directory. | `uv run dotenv run pytest tests/` |
| **`db-stop`** | Stops the running PostgreSQL container without removing the data volumes, preserving current data. | `docker compose stop` |
| **`schema`** | Generate a markdown formatted schema diagram and writes it to **`SCHEMA.md`**. | `uv run dotenv run python -m src.print_schema > SCHEMA.md` |