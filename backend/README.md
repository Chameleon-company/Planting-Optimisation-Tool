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
- `role`: One of `officer`, `supervisor`, or `admin` (optional, defaults to `officer`)

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
| `/users/{user_id}` | GET | SUPERVISOR | Get user by ID |
| `/users/{user_id}` | PUT | ADMIN | Update user information |
| `/users/{user_id}` | DELETE | ADMIN | Delete user account |
| `/farms/` | POST | OFFICER | Create new farm |
| `/farms/{farm_id}` | GET | OFFICER | Read farm by ID (ownership verified) |
| `/species/` | POST | SUPERVISOR | Create new species |
| `/environmental-profile/` | POST | OFFICER | Get environmental profile |
| `/sapling-estimation/` | POST | OFFICER | Calculate sapling estimation |
| `/recommendations/` | POST | OFFICER | Generate recommendations |
| `/recommendations/{farm_id}` | GET | OFFICER | Get farm recommendations |

Notes:

- Due to hierarchical permissions, higher roles can access lower-level endpoints
- ADMIN can access SUPERVISOR and OFFICER endpoints
- SUPERVISOR can access OFFICER endpoints
- Protected endpoints return `403 Forbidden` if the user lacks required permissions

**Key Files:**

- [src/services/authentication.py](src/services/authentication.py): Password hashing, JWT validation, role checking
- [src/models/user.py](src/models/user.py): User model with role field
- [src/models/audit_log.py](src/models/audit_log.py): Audit log model for security events
- [src/routers/auth.py](src/routers/auth.py): Login and authentication endpoints

## Limitations & Future Improvements

This section documents current system limitations, validation behaviour, and areas identified for future improvement. These points reflect **observed behaviour** in the existing implementation.

---

### Password Validation

- Passwords must be at least 8 characters long.
- Shorter passwords are rejected during request validation.
- The API returns **422 Unprocessable Entity** with a meaningful validation message.
- Affected endpoints:
  - `POST /auth/register`
  - `POST /users/`
  - `PUT /users/{user_id}`

**Future Improvements**
- Enforce stronger password requirements (uppercase, lowercase, numeric, special characters).
- Add password strength scoring and breach detection.

---

### Email Address Validation

- Email validation is handled by **Pydantic `EmailStr`**.
- Most malformed email formats are rejected with **422 validation errors**.
- Structural validation only:
  - No domain or MX record verification
  - Disposable or temporary email providers are allowed

**Future Improvements**
- Domain verification
- Email confirmation workflow
- Blocking disposable email providers

---

### Duplicate Email Handling

- Email addresses must be unique across the system.
- Attempting to register with an existing email returns **400 – "Email already registered"**.
- Affected endpoints:
  - `POST /auth/register`
  - `POST /users/`
  - `PUT /users/{user_id}`

---

### Duplicate Name Constraint

- User names must be globally unique.
- Two users cannot share the same name, even if they belong to different farms.
  - Example:
    - `"John Smith"` at Farm A → allowed
    - `"John Smith"` at Farm B → rejected
- Duplicate names are not pre-validated and result in a database integrity error.
- Affected endpoints:
  - `POST /auth/register`
  - `POST /users/`
  - `PUT /users/{user_id}`

**Future Improvements**
- Scope name uniqueness per farm or organisation.
- Add user-friendly error handling for duplicate names.

---

### Case Sensitivity – Email and Name

- Email and name fields are case-sensitive.
  - `"admin@example.com"` ≠ `"Admin@example.com"`
  - `"John Smith"` ≠ `"john smith"`
- Duplicate users can exist if casing differs.
- This can lead to login confusion and inconsistent identity handling.
- Affected endpoints:
  - `POST /auth/register`
  - `POST /users/`
  - `POST /auth/token`
  - `PUT /users/{user_id}`

**Future Improvements**
- Normalize email addresses to lowercase.
- Normalize names to a standard format before storage and lookup.

---

### Role Validation

- Role values accept any string.
- Users can be assigned invalid roles (e.g. `"oficer" or "adminn"`).
- Users with invalid roles can authenticate successfully but are blocked from protected endpoints (403 Forbidden).
- Affected endpoints:
  - `POST /auth/register`
  - `POST /users/`
  - `PUT /users/{user_id}`

**Future Improvements**
- Enforce valid role enums at the API and database levels.

---

### Role-Based Access Control Limitation

- Any authenticated user (including officers) can create new users with any role via `POST /users/`.
- Officers can create admin-level accounts despite role restrictions elsewhere.
- This allows role hierarchy to be bypassed.
- Affected endpoint:
  - `POST /users/`

**Future Improvements**
- Restrict user creation based on role hierarchy or admin-only access.

---

### User Self-Access Limitation

- Officers cannot access `GET /users/{user_id}`, even for their own user ID.
- Users must access their own profile via `GET /auth/users/me`.
- Affected endpoint:
  - `GET /users/{user_id}`

**Future Improvements**
- Allow self-access via `/users/{user_id}` or redirect to `/auth/users/me`.

---

### Placeholder Admin Endpoint

- `GET /auth/users/me/items` returns hardcoded placeholder data:
  ```json
  [
    {
      "item_id": "Foo",
      "owner": "<admin name>"
    }
  ]


### Testing
The [pytest](https://docs.pytest.org/en/stable/) v2 framework handles all of the backend test suite, current tests are in `tests/` and are mainly focused on database operations and integrity checks.

Directly running `backend $ uv run pytest` will <u>**not**</u> work, because the `just test` target replicates the current live database to a standalone test database and then performs the tests on the test database to ensure data integrity of the live database.

**Authentication Test Coverage:**

- [tests/test_auth.py](tests/test_auth.py): User registration, login, duplicate email prevention, password validation (min 8 chars), token authentication
- [tests/test_roles.py](tests/test_roles.py): Role-based permissions (Officer/Supervisor/Admin), hierarchical access control, user CRUD operations by role

**Test User Creation:**

The [src/scripts/create_test_user.py](src/scripts/create_test_user.py) script creates a test user with ADMIN role for development and testing. The script was updated to include the `role` field (set to "admin") to provide full system access for testing all endpoints. Test credentials: `testuser123@test.com` / `password123`.

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