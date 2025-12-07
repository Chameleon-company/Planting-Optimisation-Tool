# Project Command References
## 1. Virtual Environment & Dependencies

These commands establish the isolated Python environment and install all necessary packages.
| Command |	Purpose | Step |
|---|---|---|
|`uv venv`|	Creates the isolated Python virtual environment (.venv). (Only done once). | Setup |
|`uv sync`|	Reads pyproject.toml and installs all dependencies into the .venv. | Setup/Updates |
|`source .venv/bin/activate`|	Activates the virtual environment, making the installed package executables (alembic, pytest) available in the terminal. | Pre-Execution |
|`deactivate`|	Exits the virtual environment and returns to the system shell. | Cleanup | 

## 2. Database Container Management

These commands use Docker to manage the PostgreSQL database instance.
| Command |	Purpose | Step |
|---|---|---|
|`docker compose up -d`| Creates (if necessary) and starts the PostgreSQL service (pot_postgres_db) in the background (-d). | Pre-Execution |
|`docker compose down` | Stops and removes the database container and its network. (Use this for a clean shutdown). | Cleanup |
| `docker exec -it pot_postgres_db psql -U postgres -d POT_db` | Opens an interactive command-line shell (psql) inside the running container for direct database inspection. | Debugging/Inspection |

## 3. Alembic Migrations & Schema

These commands manage the evolution of the database schema.
| Command |	Purpose | Step |
|---|---|---|
| `uv run dotenv run alembic revision --autogenerate -m "..."` | Detects changes in SQLAlchemy models and generates a new migration script file in the alembic/versions/ directory. | Schema Development |
| `alembic upgrade head` | Applies all outstanding migration scripts up to the most recent one (head), creating or altering tables in the database. | Core Execution |
| ` alembic stamp <revision_id>` | Forces the database's alembic_version table to record a specific revision ID without running any SQL. (Used to fix broken history). | Debugging/Recovery |

## 4. Development & Debugging Utilities

These commands are used to check, verify, and document the backend components.
| Command | Purpose | Step |
|---|---|---|
| `uv run dotenv run pytest` | Executes the test suite, ensuring code quality and infrastructure stability (requires configuration). | Testing |
| `python backend/src/print_schema.py > SCHEMA.md` | Executes print_schema.py script to output the current SQLAlchemy schema definition into a formatted Markdown file. | Documentation |