# Backend

## Getting started
Most of the general information on getting started with the project is in [CONTRIBUTING.md](../CONTRIBUTING.md)

Fork and Clone the repository first, instructions [here](https://github.com/Chameleon-company/Planting-Optimisation-Tool/blob/master/CONTRIBUTING.md#1-fork-and-clone-the-repository)

Backend specific prerequisites:

Make sure [uv](https://docs.astral.sh/uv/getting-started/installation/) is installed, confirm with:
```bash
backend $ uv
An extremely fast Python package manager.

Usage: uv [OPTIONS] <COMMAND>
...
```
Use uv to install `python` version for the project and fetch the project dependencies.
```bash
$ cd Planting-Optimisation-Tool/backend
backend $ uv python install     # to install the python version defined in pyproject.toml
backend $ uv sync               # to install the projects dependencies
```

Docker is needed to create the database container and must be running.

#### Windows:

Download and install Docker Desktop:

https://docs.docker.com/desktop/setup/install/windows-install/

Ensure it is open and running before proceeding


#### Linux/macOS:
https://docs.docker.com/get-started/get-docker/
```bash
backend $ docker compose version
Docker Compose version v2.40.3-desktop.1
```


Make sure [just](https://github.com/casey/just) is installed, confirm with:
```bash
backend $ just help
Available recipes:
    erd              # Generates an Entity-Relationship Diagram of the current database
    help             # Displays all available justfile targets
    kill-api         # Stops the API server
    ...
```

Optionally, install [pre-commit](https://pre-commit.com/#install) for ease-of-use:
```bash
backend $ uv sync   # to install project dependencies
backend $ uv run pre-commit --version
pre-commit 4.5.1
backend $ uv run pre-commit install
pre-commit installed at .git/hooks/pre-commit
backend $ uv run pre-commit run --all-files # dry run to confirm successful installation.
```

Activating the virtual environment (required for switching between uv projects)
```bash
backend $ source .venv/bin/activate     # Activates the virtual environment
backend $ deactivate                    # Deactivates the virtual environment, needed for swapping between backend and other teams
...
backend $ cd ../datascience             # Switch to the datascience project (for example)
backend $ source .venv/bin/activate     # Activate the virtual environment of that uv project
```
an `.env` file must be present including:
- PostgreSQL user credentials
- PostgreSQL database live and test database URLs, must include `+asyncpg` driver.

`.env.example` has been included in the repository, and an `.env` file will be created via the `ensure-env` target when a [just](#justfile-commands) command is run for the first time.

To successfully run the `generate_environmental_profile` feature from the `GIS` subdirectory, a Google Earth Engine service account must be registered (keys included in handover documentation).

#### Once this is complete, please proceed to [justfile](#justfile-commands) for initial data ingestion.

## Folder structure:

```bash
backend/
├── alembic/                # Database migration scripts and history
│   └── versions/           # Migration files
├── init-db/                # Initial SQL scripts for container setup
├── src/                    # Main application source code
│   ├── domains/            # Domain data contracts for integration layer with sub-projects
│   ├── keys/               # Service account credentials
│   ├── models/             # SQLAlchemy database models
│   ├── routers/            # FastAPI route definitions (API endpoints)
│   ├── schemas/            # Pydantic models for data validation
│   ├── scripts/            # Scripts for initial database ingestion
│   │   └── data/           # Seeding data for scripts
│   └── services/           # Service layer connectivity
└── tests/                  # Pytest suite for automated testing
├── ERD.md                  # Entity-Relationship Diagram of current database
├── README.md               # This file
├── SCHEMA.md               # Current database schema
├── alembic.ini             # Alembic configuration file
├── docker-compose.yaml     # Configuration file for the database container
├── justfile                # Command runner for common project tasks/shortcuts
├── pyproject.toml          # Project metadata and dependencies list
└── uv.lock                 # Lockfile for python dependencies
```


## Infrastructure

### Database
The database is a [containerized PostGIS](https://postgis.net/documentation/getting_started/install_docker/) image - defined in `docker-compose.yaml`.

The database tables are mapped by [SQLAlchemy](https://www.sqlalchemy.org/) and the models of the tables along with their relationships are defined in `src/models/`.
The database is fully asynchronous for non-blocking I/O and supported by the API, however the service-layer logic being imported (from other teams) is mostly synchronous.

Some of the non-required PostGIS extensions bundled with the image are removed by `init-db/01-remove-extensions.sql` on initial creation.

The database migrations are handled by alembic and frequently used commands are defined in the [justfile](justfile).

Revisions are stored in alembic/versions and are timestamped with a revision message, defined in `alembic.ini`, and the PostGIS-owned tables have been excluded in `alembic/env.py` so that alembic doesn't try to alter them and break the database.

Validation of data going in and out of the database is managed by [pydantic](https://docs.pydantic.dev/latest/), the object contracts defined in `src/schemas/` ensure that the data types, range, and suitable exposure to the end-user are always as expected.
Spatial Validation: Farm boundary files in `src/models/boundaries/` are validated such that incoming GeoJSON-like structures are well-formed before they hit the GeoAlchemy2 layer.

### API
The API has been built with [FastAPI](https://fastapi.tiangolo.com/) with the endpoints defined in `src/routers/`.
Commonly used operations of the API have been covered in the [justfile](#justfile-commands) for ease-of-use. 


### Testing
The [pytest](https://docs.pytest.org/en/stable/) v2 framework handles all of the backend test suite, current tests are in `tests/` and are mainly focused on database operations and integrity checks.

Directly running `backend $ uv run pytest` will <u>**not**</u> work, because the `just test` target replicates the current live database to a standalone test database and then performs the tests on the test database to ensure data integrity of the live database.

### CI (Continuous integration testing)
`Planting-Optimisation-Tool/.github/workflows/backend-ci.yml` is the GitHub actions workflow file that runs on a new pull request.

It performs validation checks and tests to ensure they are no breaking changes being introduced to the repository, the steps are:
- Create the database in the virtual CI runner environment
- Install uv
- Install python
- Install project dependencies
- Enable the PostGIS extension
- Migrate the database (using `alembic_versions` migration files)
- Seed reference data to CI database (Hardcoded `soil_textures`)
- Replicate database
- Sync sequence values to test db
- Lint and format (with [Ruff](https://docs.astral.sh/ruff/))
- Run pytest suite on test database

## Style Guide

Linting and Formatting is handled by [Ruff](https://docs.astral.sh/ruff/) with options defined in `pyproject.toml`.

Absolute imports are highly-recommended for readability and maintainability, but code needs to be refactored to enforce.

## Just

### Install [just](https://github.com/casey/just) using:

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
| **`help`** | Shows all available `just` commands | `just --list`. Iterates over all targets and outputs to the terminal |
| **`stop`** | Stops the PostgreSQL container. | `docker compose down` |
| **`start`** | Starts the PostgreSQL container service in detached mode. | 1. `docker compose up -d` <br> 2. `sleep 5` |
| **`reset`** | Destroys existing database volume and starts new (via `start`) | 1. `docker compose down -v` <br> 2. `docker compose up -d db` | 
| **`setup`** | Initializes the database container from scratch (`stop`, `start`, `migrate`), starts the service and applies all pending Alembic migrations. | 1. `docker compose down` (via `stop`)<br> 2. `docker compose up -d db` (via `start`)<br> 3. `sleep 5` <br> 4. **`uv run dotenv run alembic upgrade head` (via `migrate`)** |
| **`revision`** | **GENERATES** a new Alembic migration script based on changes detected in your Python models. **Requires `M="message"`**. After running, you must **review the script** before running `just migrate`. | `uv run dotenv run alembic revision --autogenerate -m "message"` |
| **`migrate`** | Applies any pending Alembic migration scripts to upgrade the database schema to the latest version. This is the final step after creating and reviewing a script. | `uv run dotenv run alembic upgrade head` |
| **`populate`** | Wipes the DB, migrates, and ingests all CSV data. Outputs state of database setup statistics to terminal | Runs `setup_import_db.py` |
| **`test`** | Executes the full test suite using Pytest on the contents of the `tests/` directory. | `uv run dotenv run pytest tests/` |
| **`schema`** | Generates a markdown formatted schema diagram and writes it to **`SCHEMA.md`**. | `uv run dotenv run python -m src.generate_schema > SCHEMA.md` |
| **`erd`** | Generates a mermaid Entity-Relationship Diagram of the database and outputs to **`ERD.md`**. | `uv run dotenv run python -m src.generate_erd` |
| **`psql`** | Starts an interactive psql DB session | `docker exec -it pot_postgres_db psql -U postgres -d POT_db` |
| **`kill-api`** | Kills the API server running on port 8080 <br> Because `just populate` starts the api in the background for ease-of-use. | `uv run -m src.scripts.kill-api` |

### Initial ingestion and setup
```bash
backend $ just setup        # setup the database
backend $ just populate     # run ingestion scripts and populate the database
backend $ just test         # replicate live database to testing database
backend $ just run-api      # run the FastAPI server
```