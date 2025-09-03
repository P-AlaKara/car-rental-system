"""
Migration script to add license_state and license_class fields to users table.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def run_migration():
    """Add license_state and license_class columns to users table."""
    app = create_app()
    
    with app.app_context():
        try:
            # Add license_state column
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN license_state VARCHAR(50)
            """))
            
            # Add license_class column  
            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN license_class VARCHAR(20)
            """))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            print("   - Added license_state column to users table")
            print("   - Added license_class column to users table")
            
        except Exception as e:
            db.session.rollback()
            # Check if columns already exist
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️ Columns already exist, skipping migration")
            else:
                print(f"❌ Migration failed: {str(e)}")
                raise

if __name__ == '__main__':
    run_migration()