"""
Idempotent migration to add users.license_state and users.license_country columns
if they are missing.

This script is safe to run multiple times. It will check existing columns first
and, when available (PostgreSQL), use IF NOT EXISTS.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


def _get_dialect_name() -> str:
    try:
        bind = db.session.get_bind()
        if bind is not None:
            return bind.dialect.name
    except Exception:
        pass
    try:
        return db.engine.dialect.name
    except Exception:
        return 'postgresql'


def run_migration() -> None:
    app = create_app()
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            dialect_name = _get_dialect_name()

            # Prepare column add statements per dialect
            if dialect_name in ('postgresql', 'postgres'):
                sql_add_license_state = 'ALTER TABLE users ADD COLUMN IF NOT EXISTS license_state VARCHAR(50)'
                sql_add_license_country = 'ALTER TABLE users ADD COLUMN IF NOT EXISTS license_country VARCHAR(100)'
            else:
                sql_add_license_state = 'ALTER TABLE users ADD COLUMN license_state VARCHAR(50)'
                sql_add_license_country = 'ALTER TABLE users ADD COLUMN license_country VARCHAR(100)'

            # Add users.license_state if missing
            if 'license_state' not in existing_columns:
                print('Adding users.license_state column...')
                db.session.execute(text(sql_add_license_state))
            else:
                print('ℹ️ users.license_state already exists; skipping.')

            # Refresh column list only if needed for non-IF NOT EXISTS dialects
            if dialect_name not in ('postgresql', 'postgres'):
                existing_columns = [col['name'] for col in inspector.get_columns('users')]

            # Add users.license_country if missing
            if 'license_country' not in existing_columns:
                print('Adding users.license_country column...')
                db.session.execute(text(sql_add_license_country))
            else:
                print('ℹ️ users.license_country already exists; skipping.')

            db.session.commit()
            print('✅ Migration completed successfully.')
        except Exception as e:
            db.session.rollback()
            print(f'❌ Migration failed: {e}')
            raise


if __name__ == '__main__':
    run_migration()

