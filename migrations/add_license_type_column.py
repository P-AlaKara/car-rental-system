"""
Idempotent migration to add users.license_type column if it's missing.

Why this exists: an earlier migration attempted to add several columns in one
transaction and would abort if any one already existed. That could leave
license_type missing while the migration prints that columns already exist.
This script fixes just that column safely.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


def run_migration() -> None:
    app = create_app()
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            if 'license_type' in existing_columns:
                print('ℹ️ users.license_type already exists; nothing to do.')
                return

            # Prefer dialect-native IF NOT EXISTS when available (PostgreSQL)
            dialect_name = None
            try:
                bind = db.session.get_bind()
                if bind is not None:
                    dialect_name = bind.dialect.name
            except Exception:
                dialect_name = None
            if not dialect_name:
                try:
                    dialect_name = db.engine.dialect.name
                except Exception:
                    dialect_name = 'postgresql'

            if dialect_name in ('postgresql', 'postgres'):
                sql = 'ALTER TABLE users ADD COLUMN IF NOT EXISTS license_type VARCHAR(20)'
            else:
                sql = 'ALTER TABLE users ADD COLUMN license_type VARCHAR(20)'

            print('Adding users.license_type column...')
            db.session.execute(text(sql))
            db.session.commit()
            print('✅ Added users.license_type column successfully.')
        except Exception as e:
            db.session.rollback()
            print(f'❌ Failed to add users.license_type: {e}')
            raise


if __name__ == '__main__':
    run_migration()

