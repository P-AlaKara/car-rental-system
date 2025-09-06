"""
Migration: Repair car category enum and normalize existing data values.

This script handles cases where data was previously set to mixed-case values
such as 'SEDAN' while the Python Enum and intended PostgreSQL enum labels are
lowercase ('hatchback','sedan','suv','coupe'). It will:

1) Detect database engine (supports PostgreSQL and SQLite).
2) For PostgreSQL:
   - Ensure the target lowercase labels exist by rebuilding the enum safely.
   - Rebuild flow (idempotent):
       a. Create a temporary enum type with the correct labels if needed.
       b. Alter the `cars.category` column to the temporary type via USING cast.
       c. Drop the old enum type if safe, then recreate with correct labels.
       d. Alter the column back to the final enum type.
3) Normalize all existing `cars.category` values to valid lowercase labels,
   mapping any unknown or legacy values to 'sedan'.
4) Print counts before and after.

Safe to run multiple times.
"""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


# Target set of valid labels as stored in DB (must match Python Enum values in app.models.car)
VALID_LABELS = (
    'hatchback',
    'sedan',
    'suv',
    'coupe',
)


def _print_counts(label: str) -> None:
    try:
        rows = db.session.execute(
            text('SELECT category, COUNT(*) FROM cars GROUP BY category ORDER BY category')
        ).fetchall()
        print(label)
        for category, count in rows:
            print(f"  - {category}: {count}")
    except Exception as e:
        print(f"⚠️  Could not list categories: {e}")


def _normalize_data_values() -> None:
    """Normalize all car.category values to lowercase valid labels.

    Unknown or invalid values are coerced to 'sedan'.
    """
    # Build CASE mapping for common variants; default to 'sedan'
    variants = set([
        'HATCHBACK', 'hatchback', 'Hatchback',
        'SEDAN', 'sedan', 'Sedan',
        'SUV', 'suv', 'Suv',
        'COUPE', 'coupe', 'Coupe',
    ])

    # Generate CASE statements mapping each variant to lowercase
    case_when = []
    for v in sorted(variants):
        case_when.append(f"WHEN category = '{v}' THEN '{v.lower()}'")
    case_sql = " ".join(case_when)

    sql = text(
        f"""
        UPDATE cars
        SET category = CASE {case_sql} ELSE 'sedan' END
        """
    )
    result = db.session.execute(sql)
    db.session.commit()
    updated = getattr(result, 'rowcount', None)
    if updated is None or updated < 0:
        print('✅ Normalization completed. (Rowcount not available)')
    else:
        print(f"✅ Normalized {updated} rows to valid lowercase categories.")


def _rebuild_postgres_enum_if_needed() -> None:
    """Rebuild the PostgreSQL enum to ensure it matches lowercase VALID_LABELS.

    We perform a safe type swap via a temporary enum type.
    """
    with db.engine.begin() as conn:
        # Detect existing enum labels
        existing_values = []
        try:
            rows = conn.execute(
                text(
                    """
                    SELECT e.enumlabel
                    FROM pg_type t
                    JOIN pg_enum e ON t.oid = e.enumtypid
                    WHERE t.typname = :type_name
                    ORDER BY e.enumsortorder
                    """
                ),
                {"type_name": "carcategory"},
            ).fetchall()
            existing_values = [r[0] for r in rows]
        except Exception:
            # If type does not exist yet, nothing to rebuild here
            existing_values = []

        # Decide whether rebuild is required
        needs_rebuild = False
        if set(existing_values) != set(VALID_LABELS):
            needs_rebuild = True

        if not needs_rebuild:
            print('ℹ️  PostgreSQL enum carcategory already matches target labels.')
            return

        print('🔧 Rebuilding PostgreSQL enum carcategory to match lowercase labels...')

        # Create a temporary enum type with the correct labels
        conn.execute(text("DROP TYPE IF EXISTS carcategory_tmp"))
        conn.execute(
            text(
                "CREATE TYPE carcategory_tmp AS ENUM (:h, :s, :v, :c)"
            ),
            {"h": 'hatchback', "s": 'sedan', "v": 'suv', "c": 'coupe'},
        )

        # First ensure data values are convertible (normalize before altering type)
        _normalize_data_values()

        # Alter column to use the temporary enum via cast from text
        conn.execute(
            text(
                """
                ALTER TABLE cars
                ALTER COLUMN category TYPE carcategory_tmp
                USING category::text::carcategory_tmp
                """
            )
        )

        # Drop the original type and recreate with correct labels
        conn.execute(text("DROP TYPE IF EXISTS carcategory"))
        conn.execute(
            text("CREATE TYPE carcategory AS ENUM (:h, :s, :v, :c)"),
            {"h": 'hatchback', "s": 'sedan', "v": 'suv', "c": 'coupe'},
        )

        # Switch column back to the final type
        conn.execute(
            text(
                """
                ALTER TABLE cars
                ALTER COLUMN category TYPE carcategory
                USING category::text::carcategory
                """
            )
        )

        # Cleanup temporary type
        conn.execute(text("DROP TYPE IF EXISTS carcategory_tmp"))

        print('✅ PostgreSQL enum carcategory rebuilt successfully.')


def run_migration(config_name: str | None = None) -> None:
    import os as _os
    if config_name is None:
        config_name = _os.environ.get('MIGRATION_CONFIG') or 'default'
    app = create_app(config_name)
    with app.app_context():
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        if 'cars' not in existing_tables:
            print('ℹ️  Table `cars` does not exist; nothing to update.')
            return

        _print_counts('Current distinct categories before migration:')

        # Handle engine-specific enum repair
        engine_name = db.engine.dialect.name
        if engine_name == 'postgresql':
            _rebuild_postgres_enum_if_needed()
        else:
            # SQLite or others: just normalize values
            _normalize_data_values()

        # Always run normalization once more after enum work, to be safe
        _normalize_data_values()

        _print_counts('Distinct categories after migration:')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Fix car category enum and data')
    parser.add_argument('--config', default=None, help='Flask config name to use (default/development/testing/production)')
    args = parser.parse_args()
    run_migration(args.config)

