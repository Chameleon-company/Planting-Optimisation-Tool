# Backend

## Getting Started
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
backend $ uv sync               # to install the project's dependencies
```

Docker is needed to create the database container and must be running.

#### Windows:

Download and install Docker Desktop:

https://docs.docker.com/desktop/setup/install/windows-install/

Ensure it is open and running before proceeding

**⚠️ Windows users: If you have Postgres installed natively, it will conflict with the Docker container on port 5432. Either disable it (Stop-Service postgresql*) or change the Docker port to 5433 before running `just setup`.**


#### Linux/macOS:
https://docs.docker.com/get-started/get-docker/
```bash
backend $ docker compose version
Docker Compose version v2.40.3-desktop.1
```


Make sure [just](https://github.com/casey/just) is installed, confirm with:
```bash
backend $ just --list
Available recipes:
    erd              # Generates an Entity-Relationship Diagram of the current database
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
An `.env` file must be present containing:
- PostgreSQL user credentials
- PostgreSQL database live and test database URLs, must include `+asyncpg` driver.

`.env.example` has been included in the repository, and an `.env` file will be created via the `ensure-env` target when a [just](#justfile-commands) command is run for the first time.

To successfully run the `generate_environmental_profile` feature from the `GIS` subdirectory, a Google Earth Engine service account must be registered (service account details included in handover documentation).

#### Once this is complete, please proceed to [justfile](#justfile-commands) for initial data ingestion.

## Folder Structure

```bash
backend/
├── alembic/                    # Alembic migration configuration and history
│   ├── versions/               # Database migration files
│   ├── README                  # Alembic default documentation
│   ├── env.py                  # Alembic environment configuration
│   └── script.py.mako          # Alembic migration template
│
├── docs/                       # Backend documentation
│
├── init-db/                    # Database initialisation SQL scripts
│   └── 01-remove-extensions.sql
│
├── locust/                     # Load testing utilities
│
├── src/                        # Python src-layout application package
│   ├── domains/                # Domain contracts and integration models
│   ├── models/                 # SQLAlchemy ORM database models
│   ├── routers/                # FastAPI route endpoints
│   ├── schemas/                # Pydantic request/response schemas
│   ├── scripts/                # Utility and ingestion scripts
│   ├── services/               # Business logic and service layer
│   ├── utils/                  # Shared utility helpers
│   ├── cache.py                # Redis caching utilities
│   ├── config.py               # Application configuration
│   ├── database.py             # Database connection setup
│   ├── dependencies.py         # Shared FastAPI dependencies
│   ├── generate_erd.py         # ERD generation script
│   ├── generate_schema.py      # Schema documentation generator
│   └── main.py                 # FastAPI application entry point
│
├── tests/                      # Automated pytest suite
│   ├── models/                 # Model tests
│   ├── routes/                 # API route tests
│   ├── schemas/                # Schema validation tests
│   ├── services/               # Service layer tests
│   ├── conftest.py             # Shared pytest fixtures
│   └── test_*.py               # Integration and feature tests
│
├── .env.example                # Example environment variables
├── .gitignore
├── .python-version
├── Dockerfile                  # Backend container configuration
├── ERD.md                      # Entity Relationship Diagram
├── README.md                   # Backend documentation
├── SCHEMA.md                   # Generated database schema documentation
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Docker service configuration
├── justfile                    # Task runner commands
├── package-lock.json
├── pyproject.toml              # Python dependencies and project config
└── uv.lock                     # Dependency lock file
```


## Infrastructure

### Database
The database is a [containerized PostGIS](https://postgis.net/documentation/getting_started/install_docker/) image - defined in `docker-compose.yml`.

The database tables are mapped by [SQLAlchemy](https://www.sqlalchemy.org/) and the models of the tables along with their relationships are defined in `src/models/`.
The backend uses asynchronous SQLAlchemy sessions and FastAPI endpoints for non-blocking database operations, while some imported GIS and data-processing workflows remain synchronous due to computational processing requirements.

Some of the non-required PostGIS extensions bundled with the image are removed by `init-db/01-remove-extensions.sql` on initial creation.

Database migration workflows and Alembic usage guidelines are documented in [`docs/database-migration-workflow.md`](docs/database-migration-workflow.md).

Revisions are stored in alembic/versions and are timestamped with a revision message, defined in `alembic.ini`, and the PostGIS-owned tables have been excluded in `alembic/env.py` so that alembic doesn't try to alter them and break the database.

Validation of data going in and out of the database is managed by [pydantic](https://docs.pydantic.dev/latest/), the object contracts defined in `src/schemas/` ensure that the data types, range, and suitable exposure to the end-user are always as expected.
Spatial Data Handling: Farm boundary geometries are represented using GeoAlchemy2 spatial models with PostGIS `MULTIPOLYGON` support.

### API
The API has been built with [FastAPI](https://fastapi.tiangolo.com/) with the endpoints defined in `src/routers/`.
Commonly used operations of the API have been covered in the [justfile](#justfile-commands) for ease-of-use.

#### Authentication & Authorization

The application uses JWT (JSON Web Token) based authentication with role-based access control (RBAC).

**Authentication Flow:**

1. User logs in with email and password via `/auth/token` endpoint
2. Password is verified against bcrypt hash in database
3. JWT access token is returned for subsequent requests
4. Token is sent in `Authorization: Bearer <token>` header

**User Roles (Hierarchical):**

- `officer` (level 1): Basic user permissions
- `supervisor` (level 2): Can view/manage users and resources
- `admin` (level 3): Full system access

Higher roles inherit all permissions of lower roles.

**Detailed Role Permissions:**

**OFFICER (Level 1) - Basic User:**

Can:

- Create and view their own farms (ownership-based access control)
- Generate environmental profiles for farm locations
- Calculate sapling estimations
- Generate and view planting recommendations
- Create new user accounts (any role - requires authentication)
- View their own profile information

Cannot:

- List or view other users' information
- Update or delete any user accounts
- Create new species in the system
- Access farms owned by other users

**SUPERVISOR (Level 2) - User Manager:**

Can (in addition to all Officer permissions):

- List all users in the system
- View detailed information of any user
- Create new species entries

Cannot:

- Update user information (including passwords and roles)
- Delete user accounts

**ADMIN (Level 3) - Full Administrator:**

Can (in addition to all Supervisor and Officer permissions):

- Update any user's information (email, name, password, role)
- Delete user accounts
- Full unrestricted access to all system endpoints

Cannot:

- Nothing - administrators have complete system access

**Security Features:**

- Passwords hashed with bcrypt (never stored in plain text)
- JWT tokens for stateless authentication
- Role-based permission checks via `require_role()` dependency
- Audit logging for security events (login, user modifications, etc.)

**User Registration:**

To register a new user, send a POST request to `/auth/register`:

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123",
  "role": "officer"
}
```

- `email`: Valid email address (required, must be unique)
- `name`: User's full name (required)
- `password`: Password with minimum 8 characters (required)
- `role`: User role (defaults to `officer` if not provided)

Response returns the created user (without password):

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "officer"
}
```

**Login:**

To obtain an access token, send a POST request to `/auth/token` with form data:

```text
username=user@example.com&password=securepassword123
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests: `Authorization: Bearer <access_token>`

**Role-Based Permission Checks:**

The following endpoints have role-based access control implemented:

| Endpoint | Method | Required Role | Description |
| :--- | :--- | :--- | :--- |
| `/users/` | GET | SUPERVISOR | List all users |
| `/users/{user_id}` | GET | SUPERVISOR | Authenticated user (ownership/admin enforced) |
| `/users/{user_id}` | PUT | ADMIN | Update user information |
| `/users/{user_id}` | DELETE | ADMIN | Delete user account |
| `/farms/` | POST | OFFICER | Create new farm |
| `/farms/{farm_id}` | GET | OFFICER | Read farm by ID (ownership verified) |
| `/species/` | POST | SUPERVISOR | Create new species |
| `/profile/{farm_id}` | GET | OFFICER | Get environmental profile |
| `/sapling-estimation/calculate` | POST | OFFICER | Calculate sapling estimation |
| `/recommendations/` | POST | OFFICER | Generate recommendations |
| `/recommendations/{farm_id}` | GET | OFFICER | Get farm recommendations |
| `/reports/farm/{farm_id}` | GET | OFFICER | Get report for a single farm (ownership verified) |
| `/reports/farm/{farm_id}/export/docx` | GET | OFFICER | Download single farm report as DOCX (ownership verified) |
| `/reports/farm/{farm_id}/export/pdf` | GET | OFFICER | Download single farm report as PDF (ownership verified) |
| `/reports/farms` | GET | SUPERVISOR | Get reports for all farms under management |
| `/reports/farms/export/docx` | GET | SUPERVISOR | Download all farms under management as DOCX |
| `/reports/farms/export/pdf` | GET | SUPERVISOR | Download all farms under management as PDF |
| `/parameters` | GET | ADMIN | List all scoring parameters |
| `/parameters/{parameter_id}` | GET | ADMIN | Get a scoring parameter by ID |
| `/parameters/species/{species_id}` | GET | ADMIN | List all scoring parameters for a species |
| `/parameters` | POST | ADMIN | Create a new scoring parameter |
| `/parameters/{parameter_id}` | PUT | ADMIN | Update an existing scoring parameter |
| `/parameters/{parameter_id}` | DELETE | ADMIN | Delete a scoring parameter |
| `/ahp/calculate-and-save` | POST | ADMIN | Calculates weights and updates database |
| `/global-weights/runs` | GET | ADMIN | List the stories global weights runs |
| `/global-weights/runs/{run_id}` | GET | ADMIN | Get the global weights for a particular run |
| `/global-weights/runs/{run_id}` | DELETE | ADMIN | Delete a run |
| `/global-weights/import` | POST | ADMIN | Import a global weights run |
| `/global-weights/epi-add-scores` | POST | ADMIN | Add raw scores to uploaded EPI data and download as CSV |

Notes:

- Due to hierarchical permissions, higher roles can access lower-level endpoints
- ADMIN can access SUPERVISOR and OFFICER endpoints
- SUPERVISOR can access OFFICER endpoints
- Protected endpoints return `403 Forbidden` if the user lacks required permissions

**Key Files:**

- [src/dependencies.py](src/dependencies.py): JWT token validation, `get_current_user`, `require_role` dependency
- [src/services/authentication.py](src/services/authentication.py): Password hashing and user authentication (`authenticate_user`, `log_audit_event`)
- [src/models/user.py](src/models/user.py): User model with role field
- [src/models/audit_log.py](src/models/audit_log.py): Audit log model for security events
- [src/routers/auth.py](src/routers/auth.py): Login and authentication endpoints

---

### Password Validation

- Passwords must:
  - be at least 8 characters long
  - contain at least one uppercase letter
  - contain at least one lowercase letter
  - contain at least one number
  - contain at least one special character
- Shorter passwords are rejected during request validation.
- The API returns **422 Unprocessable Entity** with a meaningful validation message.
- Affected endpoints:
  - `POST /auth/register`
  - `POST /users/`
  - `PUT /users/{user_id}`

---

### Email Address Validation

- Email validation is handled by **Pydantic `EmailStr`**.
- Most malformed email formats are rejected with **422 validation errors**.
- Structural validation only:
  - No domain or MX record verification
  - Disposable or temporary email providers are allowed

---

### Duplicate Email Handling

- Email addresses must be unique across the system.
- Attempting to register with an existing email returns **400 – "Email already registered"**.
- Affected endpoints:
  - `POST /auth/register`
  - `POST /users/`
  - `PUT /users/{user_id}`

---

### Testing
The [pytest](https://docs.pytest.org/en/stable/) v2 framework handles all of the backend test suite, current tests are in `tests/` and are mainly focused on database operations and integrity checks.

Directly running `backend $ uv run pytest` will <u>**not**</u> work, because the `just test` target prepares the migrated local development database and replicates it into a dedicated test database before running the test suite.

**Authentication Test Coverage:**

- [tests/test_auth.py](tests/test_auth.py): User registration, login, duplicate email prevention, password validation (min 8 chars), token authentication
- [tests/test_roles.py](tests/test_roles.py): Role-based permissions (Officer/Supervisor/Admin), hierarchical access control, user CRUD operations by role

**Test User Creation:**

The [src/scripts/create_test_user.py](src/scripts/create_test_user.py) script creates a test user with ADMIN role for development and testing. The script was updated to include the `role` field (set to "admin") to provide full system access for testing all endpoints. Test credentials: `testuser123@test.com` / `password123`.

### Load Testing

[Locust](https://locust.io/) is used for load testing. Scripts are in `locust/`.

Two scenarios are defined - `MixedWorkloadUser` covers the full range of read endpoints (recommendations, sapling estimation, environmental profile, reports, farm lookups), and `HeavyConcurrentUser` hammers the most expensive bulk endpoints concurrently to identify DB locking issues.

Local:
```bash
just run-api
just seed-users        # one-time, creates 10 admin test users
just load-test
# open http://localhost:8089 - recommended: 10 users, ramp-up 2/s
```

In the cloud:
```bash
just render-seed-users
just render-load-test
# open http://localhost:8089 - recommended: 5 users, ramp-up 1/s
```

### CI (Continuous integration testing)
`Planting-Optimisation-Tool/.github/workflows/backend-ci.yml` is the GitHub actions workflow file that runs on a new pull request.

It performs validation checks and tests to ensure there are no breaking changes being introduced to the repository, the steps are:
- Create the database in the virtual CI runner environment
- Install uv
- Install python
- Install project dependencies
- Enable the PostGIS extension
- Migrate the database (using `alembic_versions` migration files)
- Seed reference data required for backend services and tests
- Replicate database
- Sync sequence values to test db
- Lint and format (with [Ruff](https://docs.astral.sh/ruff/))
- Run pytest suite on test database

## Style Guide

Refer to the project processes documentation for coding standards, linting, formatting, and development workflow conventions.

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
| **`stop`** | Stops the PostgreSQL container. | `docker compose down` |
| **`start`** | Starts the PostgreSQL container service in detached mode. | 1. `docker compose up -d` <br> 2. `sleep 5` |
| **`reset`** | Destroys existing database volume, starts fresh, and applies migrations | 1. `docker compose down -v` <br> 2. `docker compose up -d db` <br> 3. `uv run alembic upgrade head` |
| **`setup`** | Restarts the DB container and applies any pending migrations. Data volumes are preserved. | 1. `docker compose down` (via `stop`)<br> 2. `docker compose up -d db` (via `start`)<br> 3. `sleep 5` <br> 4. `uv run alembic upgrade head` (via `migrate`) |
| **`revision`** | **GENERATES** a new Alembic migration script based on changes detected in your Python models. Called as `just revision "message"`. After running, you must **review the script** before running `just migrate`. | `uv run alembic revision --autogenerate -m "message"` |
| **`migrate`** | Applies any pending Alembic migration scripts to upgrade the database schema to the latest version. This is the final step after creating and reviewing a script. | `uv run dotenv run alembic upgrade head` |
| **`populate [port]`** | Wipes the DB, migrates, and ingests all CSV data. Outputs state of database setup statistics to terminal. Accepts an optional port (default: 8080, or `API_PORT` from `.env`). Will warn and exit if the port is in use by a non-API process. | Runs `setup_import_db.py` |
| **`test`** | Executes the full test suite using Pytest on the contents of the `tests/` directory. | `uv run dotenv run pytest tests/` |
| **`schema`** | Generates a markdown formatted schema diagram and writes it to **`SCHEMA.md`**. | `uv run dotenv run python -m src.generate_schema > SCHEMA.md` |
| **`erd`** | Generates a mermaid Entity-Relationship Diagram of the database and outputs to **`ERD.md`**. | `uv run dotenv run python -m src.generate_erd` |
| **`psql`** | Starts an interactive psql DB session | `docker exec -it pot_postgres_db psql -U postgres -d POT_db` |
| **`run-api [port]`** | Starts the FastAPI development server. Accepts an optional port (default: 8080, or `API_PORT` from `.env`). | `uv run fastapi dev src/main.py` |
| **`kill-api [port]`** | Stops the API server. Only kills the process if it is running uvicorn or fastapi - will warn and skip if another process (e.g. Java) is on the port. Accepts an optional port (default: 8080, or `API_PORT` from `.env`). | `uv run -m src.scripts.kill-api` |
| **`seed-users`** | Creates 10 admin test users in the local DB for load testing. Idempotent - safe to run multiple times. | `uv run python locust/seed_users.py` |
| **`load-test [host]`** | Starts Locust against the local API. Open http://localhost:8089 to configure and start the test. Host must match the port FastAPI is running on (default: http://localhost:8080, or `API_PORT` from `.env`). | `uv run locust -f locust/locustfile.py --host <host>` |
| **`render-psql`** | Opens an interactive psql session against the Render production database. Requires `backend/.env.render`. | `psql $DATABASE_URL` |
| **`render-status`** | Lists all Render services and their current status. Requires `backend/.env.render` with `RENDER_API_KEY` set. | `render services --output json` |
| **`render-logs`** | Streams live logs from the Render backend service (Ctrl+C to stop). Requires `backend/.env.render`. | `render logs --resources $RENDER_BACKEND_ID --tail` |
| **`render-deploy`** | Triggers a manual redeploy of the Render backend service. Requires `backend/.env.render`. | `render deploy --service-id $RENDER_BACKEND_ID` |
| **`render-migrate`** | Applies pending Alembic migrations against the Render production database. Requires `backend/.env.render` with correct `DATABASE_URL`. | `uv run alembic upgrade head` |
| **`render-populate`** | Seeds reference data and creates the test user on the Render production database. Requires `backend/.env.render`. **Never run `just populate` against Render** - it wipes local Docker containers first. | Runs `seed_references.py`, `create_test_user.py`, `setup_import_db.py` |
| **`render-seed-users`** | Creates 10 admin test users in the Render DB for load testing. Requires `backend/.env.render`. | `uv run python locust/seed_users.py` (against Render DB) |
| **`render-load-test`** | Starts Locust against the Render API. Open http://localhost:8089 to configure and start the test. Requires `backend/.env.render`. | `uv run locust -f locust/locustfile.py --host $RENDER_API_URL` |

### Initial ingestion and setup
```bash
backend $ just setup        # setup the database
backend $ just populate     # run ingestion scripts and populate the database
backend $ just test         # replicate live database to testing database
backend $ just run-api      # run the FastAPI server
```
