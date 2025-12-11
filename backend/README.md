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

The migration targets (`revision`, `rename-column`, `db-apply`) are designed to separate script creation from script application, enforcing manual review for non-destructive changes.

run `make [target]` in `/backend` to execute.

| Target | Purpose | Shell Commands Executed |
| :--- | :--- | :--- |
| **`setup`** | Initializes the database container from scratch (`db-teardown`), starts the service, and applies all pending Alembic migrations. | 1. `docker compose down -v` (via `db-teardown`) 2. `docker compose up -d db` (via `db-start`) 3. `sleep 5` 4. **`uv run dotenv run alembic upgrade head` (via `db-apply`)** |
| **`db-teardown`** | Stops and removes the PostgreSQL container and all associated data volumes for a clean start. | `docker compose down -v` |
| **`db-start`** | Ensures a clean state (`db-teardown`) then starts the PostgreSQL container service in detached mode. | 1. `docker compose down -v` (via `db-teardown`) 2. `docker compose up -d db` 3. `sleep 5` |
| **`db-apply`** | **APPLIES** any pending Alembic migration scripts to upgrade the database schema to the latest version. This is the final step after creating and reviewing a script. | `uv run dotenv run alembic upgrade head` |
| **`revision`** | **GENERATES** a new Alembic migration script based on changes detected in your Python models. **Requires `M="message"`**. After running, you must **review the script** before running `make db-apply`. | `uv run dotenv run alembic revision --autogenerate -m "message"` |
| **`rename-column`** | **GUIDES** the user through generating a **manual script** to perform non-destructive column renaming. This prevents data loss from Alembic's default DROP/ADD behavior. | 1. `uv run dotenv run alembic revision -m "MANUAL_RENAME..."` 2. (Requires manual editing of script) |
| **`test`** | Executes the full test suite using Pytest on the contents of the `tests/` directory. | `uv run dotenv run pytest tests/` |
| **`db-stop`** | Stops the running PostgreSQL container without removing the data volumes, preserving current data. | `docker compose stop` |
| **`schema`** | Generates a markdown formatted schema diagram and writes it to **`SCHEMA.md`**. | `uv run dotenv run python -m src.print_schema > SCHEMA.md` |