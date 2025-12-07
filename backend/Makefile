SERVICE_NAME = db
CONTAINER_NAME = pot_postgres_db
ALEMBIC_CMD = uv run dotenv run alembic
PYTHON_PATH_ROOT = .
PYTEST_RUNNER = uv run dotenv run
PYTEST_CMD = $(PYTEST_RUNNER) pytest
UV_RUNNER = uv run dotenv run

# The primary command for a developer to set up the project from scratch.
# It depends on db-start, which transitively calls db-teardown.
setup: db-start db-migrate
	@echo "--- Setup Complete: Database is ready and migrated ---"

# Ensures the old container is stopped and removed
.PHONY: db-teardown
db-teardown:
	@echo "--- Ensuring Clean Database Teardown ---"
	docker compose down -v

# Starts a fresh container (depends on db-teardown)
.PHONY: db-start
db-start: db-teardown
	@echo "--- Starting NEW PostgreSQL Container ---"
	docker compose up -d $(SERVICE_NAME)
	sleep 5

# Applies the schema migration
.PHONY: db-migrate
db-migrate:
	@echo "--- Applying Schema Migration ---"
	$(ALEMBIC_CMD) upgrade head

# ----------------- Utility Targets -----------------

# Generate a new autogenerate revision
# Usage: make revision M="Added new column"
.PHONY: revision
revision:
	@echo "--- Generating New Migration Script ---"
	@if [ -z "$M" ]; then \
		echo "Error: Migration message not provided. Use: make revision M=\"Your message\""; \
		exit 1; \
	fi
	$(ALEMBIC_CMD) revision --autogenerate -m "$M"

# Run all tests with environment loaded
.PHONY: test
test:
	@echo "--- Running Pytest ---"
	$(PYTEST_CMD) tests/

# Stop the database without removing data volumes
.PHONY: db-stop
db-stop:
	@echo "--- Stopping PostgreSQL Container ---"
	docker compose stop

# Outputs current DB schema to SCHEMA.md from models
.PHONY: schema
schema:
	@echo "--- Generating SCHEMA.md from Models ---"
	$(UV_RUNNER) python -m src.print_schema > SCHEMA.md
	@echo "--- SCHEMA.md created ---"