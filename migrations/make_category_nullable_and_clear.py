"""
Migration: Make cars.category nullable and clear all existing values.

This script is intended primarily for PostgreSQL deployments. It will:

1) Ensure the database connection is initialized via the Flask app factory
   using the provided config name (defaults to 'default').
2) If using PostgreSQL:
   - Check if `cars.category` is NOT NULL and drop the constraint if needed.
   - Set every existing `cars.category` value to NULL.
3) If using SQLite:
   - Attempt to set values to NULL directly. If a NOT NULL constraint prevents
     this, a clear error will be printed since SQLite cannot drop NOT NULL
     constraints without a table rebuild.

The script is idempotent. Re-running it will have no harmful effects.
"""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


def _pg_is_category_not_null(conn) -> bool:
    """Return True if cars.category is defined as NOT NULL in PostgreSQL."""
    row = conn.execute(
        text(
            """
            SELECT is_nullable
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = 'cars'
              AND column_name = 'category'
            """
        )
    ).fetchone()
    if not row:
        return False
    is_nullable = row[0]
    return (is_nullable or "").upper() == "NO"


def _pg_drop_not_null_if_present(conn) -> None:
    """Drop NOT NULL on cars.category in PostgreSQL if it's present."""
    try:
        if _pg_is_category_not_null(conn):
            conn.execute(text("ALTER TABLE cars ALTER COLUMN category DROP NOT NULL"))
            print("✅ Dropped NOT NULL constraint from cars.category (PostgreSQL).")
        else:
            print("ℹ️  cars.category is already nullable (PostgreSQL).")
    except Exception as exc:
        raise RuntimeError(f"Failed to drop NOT NULL on cars.category (PostgreSQL): {exc}")


def _set_all_categories_null() -> None:
    """Set all rows' category to NULL across engines."""
    try:
        result = db.session.execute(text("UPDATE cars SET category = NULL"))
        db.session.commit()
        count = getattr(result, "rowcount", None)
        if count is None or count < 0:
            print("✅ Cleared category values (rowcount unavailable).")
        else:
            print(f"✅ Cleared category values for {count} rows.")
    except Exception as exc:
        db.session.rollback()
        raise RuntimeError(f"Failed to clear category values: {exc}")


def run_migration(config_name: str | None = None) -> None:
    import os as _os
    if config_name is None:
        config_name = _os.environ.get("MIGRATION_CONFIG") or "default"

    app = create_app(config_name)
    with app.app_context():
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        if "cars" not in existing_tables:
            print("ℹ️  Table `cars` does not exist; nothing to update.")
            return

        engine_name = db.engine.dialect.name

        if engine_name == "postgresql":
            # Perform within a transaction connection
            with db.engine.begin() as conn:
                _pg_drop_not_null_if_present(conn)
            _set_all_categories_null()
        else:
            # SQLite or others: try update first. If NOT NULL blocks it, inform user.
            try:
                _set_all_categories_null()
            except RuntimeError as exc:
                print(
                    "⚠️  SQLite path: could not set categories to NULL. "
                    "SQLite cannot drop NOT NULL without a table rebuild. "
                    f"Details: {exc}"
                )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Make cars.category nullable and clear all existing values"
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Flask config name to use (default/development/testing/production)",
    )
    args = parser.parse_args()
    run_migration(args.config)

