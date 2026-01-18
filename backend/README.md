# Not complete, just jotting notes

These commands establish the isolated Python environment and install all necessary packages.
| Command |	Purpose | Step |
|---|---|---|
|`uv venv`|	Creates the isolated Python virtual environment (.venv). (Only done once). | Setup |
|`uv sync`|	Reads pyproject.toml and installs all dependencies into the .venv. | Setup/Updates |
|`source .venv/bin/activate`|	Activates the virtual environment, making the installed package executables (alembic, pytest) available in the terminal. | Pre-Execution |
|`deactivate`|	Exits the virtual environment and returns to the system shell. | Cleanup | 


## Install [just](https://github.com/casey/just) using:


Windows:
```bash
winget install --id Casey.Just --exact
```
Linux/MacOS:
```bash
apt install just
```

## Justfile commands

run `just [target]` in `/backend` to execute.

| Target | Purpose | Shell Commands Executed |
| :--- | :--- | :--- |
| **`help`** | Shows all available `just` commands | Iterates over all targets and outputs to the terminal |
| **`stop`** | Stops the PostgreSQL container. | `docker compose down` |
| **`start`** | Ensures a clean state (`stop`) then starts the PostgreSQL container service in detached mode. | 1. `docker compose down -v` (via `stop`) 2. `docker compose up -d db` 3. `sleep 5` |
| **`setup`** | Initializes the database container from scratch (`stop`, `start`, `migrate`, ), starts the service, and applies all pending Alembic migrations. | 1. `docker compose down` (via `stop`)<br> 2. `docker compose up -d db` (via `start`)<br> 3. `sleep 5` <br> 4. **`uv run dotenv run alembic upgrade head` (via `migrate`)** |
| **`revision`** | **GENERATES** a new Alembic migration script based on changes detected in your Python models. **Requires `M="message"`**. After running, you must **review the script** before running `just migrate`. | `uv run dotenv run alembic revision --autogenerate -m "message"` |
| **`migrate`** | Applies any pending Alembic migration scripts to upgrade the database schema to the latest version. This is the final step after creating and reviewing a script. | `uv run dotenv run alembic upgrade head` |
| **`populate`** | Wipes the DB, migrates, and ingests all CSV data. Outputs state of database setup statistics to terminal | Runs `setup_import_db.py` |
| **`test`** | Executes the full test suite using Pytest on the contents of the `tests/` directory. | `uv run dotenv run pytest tests/` |
| **`schema`** | Generates a markdown formatted schema diagram and writes it to **`SCHEMA.md`**. | `uv run dotenv run python -m src.generate_schema > SCHEMA.md` |
| **`erd`** | Generates a mermaid Entity-Relationship Diagram of the database and outputs to **`ERD.md`**. | `uv run dotenv run python -m src.generate_erd` |
| **`psql`** | Starts an interactive psql DB session | `docker exec -it pot_postgres_db psql -U postgres -d POT_db` |
| **`kill-api`** | Kills the API server running on port 8080 <br> Because `just populate` starts the api in the background for ease-of-use. | `uv run -m src.scripts.kill-api` |