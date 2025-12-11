SERVICE_NAME = db
CONTAINER_NAME = pot_postgres_db
ALEMBIC_CMD = uv run dotenv run alembic
PYTHON_PATH_ROOT = .
PYTEST_RUNNER = uv run dotenv run
PYTEST_CMD = $(PYTEST_RUNNER) pytest
UV_RUNNER = uv run dotenv run

# The primary command for a developer to set up the project from scratch.
# It depends on db-start, which transitively calls db-teardown.
setup: db-start db-apply
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
.PHONY: db-apply
db-migrate:
	@echo "--- Applying Schema Migration ---"
	$(ALEMBIC_CMD) upgrade head

# ----------------- Utility Targets -----------------

# Generate a new autogenerate revision
.PHONY: revision
revision:
	@echo "--- Generating New Migration Script ---"
	@if [ -z "$M" ]; then \
		echo "Error: Migration message not provided. Use: make revision M=\"Your message\""; \
		exit 1; \
	fi
	# Step 1: Create the script (with autogenerate)
	$(ALEMBIC_CMD) revision --autogenerate -m "$M"
	@echo ""
	@echo "--- SCRIPT CREATED. NEXT ACTION REQUIRED: REVIEW/EDIT ---"
	@echo "1. Script created in alembic/versions/. Open and inspect the upgrade() function."
	@echo "2. If you renamed a column or dropped data, manually correct the script (e.g., use op.alter_column)."
	@echo ""
	@echo "3. TO APPLY THE CHANGE, RUN: make db-apply"

.PHONY: rename-column
rename-column:
	@echo "--- STARTING MANUAL RENAME PROCEDURE ---"
	@echo "1. Ensure the column name is changed ONLY in your SQLAlchemy model."
	@echo "2. Generating a BLANK revision script now (DO NOT USE --autogenerate)..."
	# Generate a manual, blank script (no --autogenerate flag)
	$(ALEMBIC_CMD) revision -m "MANUAL_RENAME_REQUIRED"
	@echo ""
	@echo "--- SCRIPT CREATED. NEXT ACTION REQUIRED: EDIT MANUALLY ---"
	@echo "3. Find the script in alembic/versions/ and manually ADD the op.alter_column command."
	@echo "   Example: op.alter_column('table', 'old', new_column_name='new', ...)"
	@echo ""
	@echo "4. TO APPLY THE RENAME, RUN: make db-apply"

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