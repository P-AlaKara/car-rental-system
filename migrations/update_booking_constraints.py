"""
Migration script to:
1) Make bookings.daily_rate nullable (drop NOT NULL)
2) Enforce bookings.license_document_url NOT NULL (after filling existing NULLs)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


def run_migration():
    app = create_app()
    with app.app_context():
        inspector = db.inspect(db.engine)
        booking_columns = {col['name']: col for col in inspector.get_columns('bookings')}

        # 1) Make daily_rate nullable
        try:
            # Postgres syntax
            db.session.execute(text('ALTER TABLE bookings ALTER COLUMN daily_rate DROP NOT NULL'))
            db.session.commit()
            print('✓ bookings.daily_rate is now NULLABLE')
        except Exception as e:
            msg = str(e).lower()
            if 'does not exist' in msg or 'no such column' in msg:
                print('ℹ️ bookings.daily_rate column not found; skipping drop NOT NULL')
            else:
                # Try SQLite compatible approach (recreate is complex; skip)
                print(f'⚠ Could not drop NOT NULL on daily_rate: {e}')
                db.session.rollback()

        # 2) Make license_document_url NOT NULL
        try:
            # Fill existing NULLs with empty string to satisfy NOT NULL constraint
            db.session.execute(text("UPDATE bookings SET license_document_url = '' WHERE license_document_url IS NULL"))
            db.session.commit()
            try:
                db.session.execute(text('ALTER TABLE bookings ALTER COLUMN license_document_url SET NOT NULL'))
                db.session.commit()
                print('✓ bookings.license_document_url is now NOT NULL')
            except Exception as e2:
                print(f'⚠ Could not set NOT NULL on license_document_url: {e2}')
                db.session.rollback()
        except Exception as e:
            print(f'⚠ Could not update NULL license_document_url values: {e}')
            db.session.rollback()


if __name__ == '__main__':
    run_migration()

