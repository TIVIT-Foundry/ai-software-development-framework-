"""
============================================================================
Alembic Migration Template
============================================================================
Revision ID: {revision_id}
Revises: {down_revision}
Create Date: {create_date}

Description: {description}
Ticket: {ticket}
Author: {author}
============================================================================
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# ── Revision identifiers ──────────────────────────────────────
revision: str = "{revision_id}"
down_revision: Union[str, None] = "{down_revision}"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ═══════════════════════════════════════════════════════════════
# UPGRADE — apply the migration forward
# ═══════════════════════════════════════════════════════════════


def upgrade() -> None:
    """Apply forward migration changes."""
    # ─── Pre-verification ──────────────────────────────────
    # Uncomment and adapt if you need to check pre-conditions:
    # conn = op.get_bind()
    # if table_exists(conn, "schema_name", "table_name"):
    #     # Already applied? Skip or raise.
    #     pass

    # ─── Schema changes ────────────────────────────────────

    # -- Example: CREATE TABLE ---------------------------------
    # op.create_table(
    #     "table_name",
    #     sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
    #     sa.Column("name", sa.String(255), nullable=False),
    #     sa.Column("description", sa.Text(), nullable=True),
    #     # Audit columns (required per framework conventions)
    #     sa.Column("record_status", sa.SmallInteger(), nullable=False, server_default="1"),
    #     sa.Column("record_creation_user", sa.String(128), nullable=True),
    #     sa.Column("record_creation_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    #     sa.Column("record_update_user", sa.String(128), nullable=True),
    #     sa.Column("record_update_date", sa.DateTime(timezone=True), nullable=True),
    #     schema="schema_name",
    # )

    # -- Example: CREATE INDEX ---------------------------------
    # op.create_index(
    #     "ix_schema_table_name",
    #     "table_name",
    #     ["name"],
    #     unique=False,
    #     schema="schema_name",
    # )

    # -- Example: ALTER TABLE — ADD COLUMN ---------------------
    # op.add_column(
    #     "table_name",
    #     sa.Column("new_column", sa.String(100), nullable=True),
    #     schema="schema_name",
    # )

    # -- Example: ALTER TABLE — ALTER COLUMN -------------------
    # op.alter_column(
    #     "table_name",
    #     "column_name",
    #     existing_type=sa.String(100),
    #     type_=sa.String(255),
    #     nullable=False,
    #     schema="schema_name",
    # )

    # -- Example: ADD FOREIGN KEY ------------------------------
    # op.create_foreign_key(
    #     "fk_table_ref",
    #     "table_name",
    #     "referenced_table",
    #     ["ref_id"],
    #     ["id"],
    #     ondelete="RESTRICT",
    #     schema="schema_name",
    # )

    # -- Example: Data migration (use with caution) ------------
    # op.execute(
    #     sa.text(
    #         """
    #         UPDATE schema_name.table_name
    #         SET new_column = 'default_value'
    #         WHERE new_column IS NULL
    #         """
    #     )
    # )

    # ─── Post-verification ─────────────────────────────────
    # Uncomment and adapt if you need to verify the change:
    # conn = op.get_bind()
    # result = conn.execute(sa.text("SELECT 1 FROM schema_name.table_name LIMIT 1"))
    # assert result.scalar() is not None, "Table creation verification failed"

    pass


# ═══════════════════════════════════════════════════════════════
# DOWNGRADE — revert the migration (rollback)
# ═══════════════════════════════════════════════════════════════


def downgrade() -> None:
    """Revert migration changes (rollback)."""
    # ─── Pre-verification ──────────────────────────────────

    # ─── Revert changes (reverse order of upgrade) ─────────

    # -- Example: DROP FOREIGN KEY -----------------------------
    # op.drop_constraint(
    #     "fk_table_ref",
    #     "table_name",
    #     schema="schema_name",
    #     type_="foreignkey",
    # )

    # -- Example: ALTER TABLE — REVERT COLUMN ------------------
    # op.alter_column(
    #     "table_name",
    #     "column_name",
    #     existing_type=sa.String(255),
    #     type_=sa.String(100),
    #     nullable=True,
    #     schema="schema_name",
    # )

    # -- Example: DROP COLUMN ----------------------------------
    # op.drop_column(
    #     "table_name",
    #     "new_column",
    #     schema="schema_name",
    # )

    # -- Example: DROP INDEX -----------------------------------
    # op.drop_index(
    #     "ix_schema_table_name",
    #     table_name="table_name",
    #     schema="schema_name",
    # )

    # -- Example: DROP TABLE -----------------------------------
    # op.drop_table(
    #     "table_name",
    #     schema="schema_name",
    # )

    # ─── Post-verification ─────────────────────────────────

    pass


# ═══════════════════════════════════════════════════════════════
# HELPERS — utility functions for migrations
# ═══════════════════════════════════════════════════════════════


def table_exists(conn, schema: str, table: str) -> bool:
    """Check if a table exists in the given schema.

    Args:
        conn: SQLAlchemy connection.
        schema: Schema name.
        table: Table name.

    Returns:
        True if the table exists.
    """
    result = conn.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = :schema AND table_name = :table
            )
            """
        ),
        {"schema": schema, "table": table},
    )
    return result.scalar()


def column_exists(conn, schema: str, table: str, column: str) -> bool:
    """Check if a column exists in the given table.

    Args:
        conn: SQLAlchemy connection.
        schema: Schema name.
        table: Table name.
        column: Column name.

    Returns:
        True if the column exists.
    """
    result = conn.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = :schema
                  AND table_name = :table
                  AND column_name = :column
            )
            """
        ),
        {"schema": schema, "table": table, "column": column},
    )
    return result.scalar()


def index_exists(conn, schema: str, index_name: str) -> bool:
    """Check if an index exists in the given schema.

    Args:
        conn: SQLAlchemy connection.
        schema: Schema name.
        index_name: Index name.

    Returns:
        True if the index exists.
    """
    result = conn.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE schemaname = :schema AND indexname = :index
            )
            """
        ),
        {"schema": schema, "index": index_name},
    )
    return result.scalar()


def constraint_exists(conn, schema: str, table: str, constraint_name: str) -> bool:
    """Check if a constraint exists in the given table.

    Args:
        conn: SQLAlchemy connection.
        schema: Schema name.
        table: Table name.
        constraint_name: Constraint name.

    Returns:
        True if the constraint exists.
    """
    result = conn.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_schema = :schema
                  AND table_name = :table
                  AND constraint_name = :constraint
            )
            """
        ),
        {"schema": schema, "table": table, "constraint": constraint_name},
    )
    return result.scalar()


# ═══════════════════════════════════════════════════════════════
# IDEMPOTENCY PATTERNS — use for safe re-runs
# ═══════════════════════════════════════════════════════════════

# Pattern: Idempotent table creation
# def upgrade():
#     conn = op.get_bind()
#     if not table_exists(conn, "my_schema", "my_table"):
#         op.create_table("my_table", ..., schema="my_schema")

# Pattern: Idempotent column addition
# def upgrade():
#     conn = op.get_bind()
#     if not column_exists(conn, "my_schema", "my_table", "new_col"):
#         op.add_column("my_table", sa.Column("new_col", ...), schema="my_schema")

# Pattern: Safe column removal (with data migration check)
# def upgrade():
#     conn = op.get_bind()
#     if column_exists(conn, "my_schema", "my_table", "old_col"):
#         # First migrate data if needed
#         # conn.execute(sa.text("UPDATE ..."))
#         op.drop_column("my_table", "old_col", schema="my_schema")
