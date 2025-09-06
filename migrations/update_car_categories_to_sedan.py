"""
Migration: Normalize legacy car categories to 'sedan'.

This script updates any rows in the `cars` table whose `category` is not one of
the currently supported values ('hatchback','sedan','suv','coupe') to 'sedan'.

Safe to run multiple times.
"""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


SUPPORTED_CATEGORIES = (
    'HATCHBACK',
    'SEDAN',
    'SUV',
    'COUPE',
)


def run_migration() -> None:
    app = create_app()
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            if 'cars' not in existing_tables:
                print('ℹ️  Table `cars` does not exist; nothing to update.')
                return

            # Show current distinct categories
            try:
                print('Current distinct categories before update:')
                rows = db.session.execute(text('SELECT category, COUNT(*) FROM cars GROUP BY category ORDER BY category')).fetchall()
                for category, count in rows:
                    print(f'  - {category}: {count}')
            except Exception as e:
                print(f'⚠️  Could not list existing categories: {e}')

            # Build and run update for any non-supported category values
            supported_list = ",".join([f"'{c}'" for c in SUPPORTED_CATEGORIES])
            sql_update = text(
                f"""
                UPDATE cars
                SET category = 'SEDAN'
                WHERE category NOT IN ({supported_list})
                """
            )

            result = db.session.execute(sql_update)
            db.session.commit()
            updated = getattr(result, 'rowcount', None)
            if updated is None or updated < 0:
                print('✅ Update completed. (Rowcount not available)')
            else:
                print(f'✅ Updated {updated} rows to category=sedan.')

            # Show categories after update
            try:
                print('Distinct categories after update:')
                rows = db.session.execute(text('SELECT category, COUNT(*) FROM cars GROUP BY category ORDER BY category')).fetchall()
                for category, count in rows:
                    print(f'  - {category}: {count}')
            except Exception as e:
                print(f'⚠️  Could not list categories after update: {e}')

        except Exception as e:
            db.session.rollback()
            print(f'❌ Migration failed: {e}')
            raise


if __name__ == '__main__':
    run_migration()

