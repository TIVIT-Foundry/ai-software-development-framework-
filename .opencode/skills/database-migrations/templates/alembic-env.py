"""
============================================================================
Alembic env.py — Configuration for PostgreSQL with SQLAlchemy 2.0 async
============================================================================
This is the Alembic environment configuration file. It sets up:
  - Database connection (sync for Alembic operations)
  - Target metadata for autogenerate
  - Migration script location and naming
  - Context configuration (online/offline mode)
  - Logging of migration execution

Usage:
  alembic revision --autogenerate -m "description"   # Create migration
  alembic upgrade head                                # Apply all migrations
  alembic downgrade -1                                # Rollback one step
  alembic current                                     # Show current revision
  alembic history                                     # Show migration history

Place this file in the migrations/ directory (not in versions/).
============================================================================
"""
import asyncio
import os
import sys
from logging.config import fileConfig
from typing import Optional

from alembic import context
from sqlalchemy import pool, engine_from_config
from sqlalchemy.ext.asyncio import create_async_engine

# ── Add project root to path (adjust if needed) ───────────────
# This ensures Alembic can import your SQLAlchemy models.
# If your project structure is different, adjust accordingly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# ── Alembic Config object ─────────────────────────────────────
# Provides access to the values within the .ini file.
config = context.config

# ── Logging configuration ─────────────────────────────────────
# Interpret the config file for Python logging.
# This sets up loggers basically from alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ═══════════════════════════════════════════════════════════════
# TARGET METADATA — import your SQLAlchemy models here
# ═══════════════════════════════════════════════════════════════
# For 'autogenerate' support, Alembic needs your Base metadata.
# Import all models so their table definitions are registered.
# Adjust the import path to match your project structure.

# -- Example: single models module --
# from app.models.base import Base
# target_metadata = Base.metadata

# -- Example: multiple model modules --
# from app.database import Base
# from app.models import user, tenant, audit  # noqa: F401 — ensure all models are imported
# target_metadata = Base.metadata

# -- Placeholder: replace with your actual import --
from app.database import Base  # noqa: E402

# Import all model modules to ensure they are registered in Base.metadata
# import app.models  # noqa: F401, E402 — uncomment and adjust as needed

target_metadata = Base.metadata

# ═══════════════════════════════════════════════════════════════
# DATABASE URL — from environment or alembic.ini
# ═══════════════════════════════════════════════════════════════
# Priority:
#   1. DATABASE_URL environment variable (recommended for production)
#   2. sqlalchemy.url in alembic.ini (for local development)
#
# For async connections, Alembic internally uses a sync engine.
# The DATABASE_URL should be in async format (postgresql+asyncpg://...).
# Alembic automatically converts it to sync for its own operations.

DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Use the async URL from environment — Alembic handles the sync conversion
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
else:
    # Falls back to the url in alembic.ini [alembic] section
    DATABASE_URL = config.get_main_option("sqlalchemy.url")


# ═══════════════════════════════════════════════════════════════
# METADATA FILTERING — include/exclude schemas
# ═══════════════════════════════════════════════════════════════
# Control which schemas are included in autogenerate.
# Exclude system schemas and include only application schemas.


def include_object(obj, name, type_, reflected, compare_to):
    """Filter objects for autogenerate.

    Excludes:
      - pgcrypto extension tables
      - Alembic's own version table
      - PostgreSQL system schemas (pg_catalog, information_schema)
      - UUID generation functions that are auto-created

    Args:
        obj: The SQLAlchemy object (Table, Column, Index, etc.).
        name: Name of the object.
        type_: Type of the object ("table", "column", "index", etc.).
        reflected: True if the object comes from database reflection.
        compare_to: The object being compared to, if any.

    Returns:
        True if the object should be included in autogenerate.
    """
    # Skip Alembic's own version table
    if type_ == "table" and name == "alembic_version":
        return False

    # Skip PostgreSQL system schemas
    if hasattr(obj, "schema") and obj.schema in (
        "pg_catalog",
        "information_schema",
    ):
        return False

    return True


# ═══════════════════════════════════════════════════════════════
# OFFLINE MODE — generate SQL without connecting to DB
# ═══════════════════════════════════════════════════════════════
# Usage: alembic upgrade head --sql > migration.sql
# This generates the raw SQL that would be executed.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # Render SQL literals instead of bind params
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        # Multi-tenancy: uncomment to include all schemas
        # include_schemas=True,
        # version_table_schema="public",
    )

    with context.begin_transaction():
        context.run_migrations()


# ═══════════════════════════════════════════════════════════════
# ONLINE MODE — connect to DB and apply migrations
# ═══════════════════════════════════════════════════════════════
# This is the standard mode used when running: alembic upgrade head


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a
    connection with the context.
    """
    # Alembic requires a synchronous connection internally.
    # If DATABASE_URL uses asyncpg, convert to psycopg2 for Alembic.

    url = config.get_main_option("sqlalchemy.url")
    sync_url = _convert_async_to_sync(url)

    # Create sync engine for Alembic
    connectable = engine_from_config(
        {"sqlalchemy.url": sync_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't pool — each migration gets its own connection
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            # Transaction per migration revision
            transaction_per_migration=True,
            # Uncomment for multi-tenancy (schema-per-tenant):
            # include_schemas=True,
            # version_table_schema="public",
            # Compare type to detect column type changes
            compare_type=True,
            # Compare server_default to detect default value changes
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════


def _convert_async_to_sync(url: str) -> str:
    """Convert an async database URL to a sync one for Alembic.

    Alembic uses synchronous DBAPI drivers internally.
    This converts postgresql+asyncpg:// → postgresql://

    Args:
        url: Database URL (may be async or sync).

    Returns:
        Sync database URL suitable for Alembic.
    """
    if not url:
        raise ValueError("DATABASE_URL is not set")

    # Map async drivers to sync equivalents
    replacements = {
        "postgresql+asyncpg": "postgresql",
        "postgresql+psycopg": "postgresql",
        "mysql+aiomysql": "mysql",
        "mysql+asyncmy": "mysql",
        "sqlite+aiosqlite": "sqlite",
    }

    for async_driver, sync_driver in replacements.items():
        if url.startswith(async_driver + "://"):
            return url.replace(async_driver, sync_driver, 1)

    # If already sync, return as-is
    return url


# ═══════════════════════════════════════════════════════════════
# MULTI-TENANCY SUPPORT (optional)
# ═══════════════════════════════════════════════════════════════
# Uncomment and adapt for schema-per-tenant migrations.
#
# def get_tenant_schemas(connection):
#     """Return list of tenant schema names from a control table."""
#     result = connection.execute(
#         sa.text("SELECT schema_name FROM public.tenants WHERE active = true")
#     )
#     return [row[0] for row in result]
#
# Then in run_migrations_online(), before context.configure():
#     tenant_schemas = get_tenant_schemas(connection)
#     for schema in tenant_schemas:
#         connection.execute(sa.text(f"SET search_path TO {schema}"))
#         context.configure(...)
#         with context.begin_transaction():
#             context.run_migrations()
#         connection.execute(sa.text("SET search_path TO public"))

# ═══════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
