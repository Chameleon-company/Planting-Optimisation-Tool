# ruff: noqa: F401,F403
from logging.config import fileConfig
import os
import sys

# Alembic's autogenerate process reads Base.metadata, not the models directly.
from src.database import Base

# Model discovery
# These imports appear 'unused' but are REQUIRED.
import src.models  # noqa: F403

# Because database.py lives above this dir we need to add path
# .. = backend, so that we can import src/ classes
sys.path.insert(0, os.path.abspath(".."))
from dotenv import load_dotenv  # For the .env file
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
load_dotenv(os.path.join(os.getcwd(), "..", ".env"))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using the asynchronous engine.
    """
    # Get the URL from .env file
    db_url = os.environ.get("DATABASE_URL")

    if db_url is None:
        raise Exception(
            "DATABASE_URL env variable is not set, ensure it's in .env file"
        )

    # Create the async Engine
    connectable = create_async_engine(
        db_url,
        echo=True,
        poolclass=pool.NullPool,
    )

    # Use a context manager to bridge the sync Alembic script to the async connection
    async def run_async_migrations():
        async with connectable.connect() as connection:
            # run sync migrations over an async connection
            await connection.run_sync(do_run_migrations)

        # Close the engine after use
        await connectable.dispose()

    # Define the sync function that configures and runs the migrations
    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            dialect_opts={"paramstyle": "named"},
        )
        with context.begin_transaction():
            context.run_migrations()

    # 5. Run the async logic using the standard asyncio library
    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
