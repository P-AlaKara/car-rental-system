#!/usr/bin/env python
"""
Script to run database migrations for the handover feature.
This adds the necessary fields and tables for vehicle handover process.
"""

import os
import sys
from app import create_app, db
from app.models import Booking, BookingPhoto, PayAdvantageCustomer, DirectDebitSchedule

def run_migrations():
    """Run database migrations to add handover fields."""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check if tables already exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # Create new tables if they don't exist
            if 'booking_photos' not in existing_tables:
                print("Creating booking_photos table...")
                BookingPhoto.__table__.create(db.engine)
                print("✓ booking_photos table created")
            else:
                print("booking_photos table already exists")
            
            if 'pay_advantage_customers' not in existing_tables:
                print("Creating pay_advantage_customers table...")
                PayAdvantageCustomer.__table__.create(db.engine)
                print("✓ pay_advantage_customers table created")
            else:
                print("pay_advantage_customers table already exists")
            
            if 'direct_debit_schedules' not in existing_tables:
                print("Creating direct_debit_schedules table...")
                DirectDebitSchedule.__table__.create(db.engine)
                print("✓ direct_debit_schedules table created")
            else:
                print("direct_debit_schedules table already exists")
            
            # Add new columns to bookings table if they don't exist
            booking_columns = [col['name'] for col in inspector.get_columns('bookings')]
            
            new_columns = {
                'license_verified': 'BOOLEAN',
                'license_verified_at': 'DATETIME',
                'contract_signed_url': 'TEXT',
                'contract_signed_at': 'DATETIME',
                'pickup_odometer': 'INTEGER',
                'return_odometer': 'INTEGER',
                'handover_completed_at': 'DATETIME',
                'handover_completed_by': 'INTEGER',
                'return_completed_at': 'DATETIME',
                'return_completed_by': 'INTEGER',
                'direct_debit_schedule_id': 'VARCHAR(100)'
            }
            
            for column_name, column_type in new_columns.items():
                if column_name not in booking_columns:
                    print(f"Adding column {column_name} to bookings table...")
                    try:
                        db.engine.execute(f'ALTER TABLE bookings ADD COLUMN {column_name} {column_type}')
                        print(f"✓ {column_name} column added")
                    except Exception as e:
                        print(f"⚠ Could not add {column_name}: {e}")
                else:
                    print(f"{column_name} column already exists in bookings table")
            
            # Create upload directories
            upload_dirs = [
                'uploads',
                'uploads/booking_photos',
                'uploads/contracts'
            ]
            
            for dir_path in upload_dirs:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    print(f"✓ Created directory: {dir_path}")
                else:
                    print(f"Directory already exists: {dir_path}")
            
            print("\n✅ All migrations completed successfully!")
            print("\nNext steps:")
            print("1. Add PAY_ADVANTAGE_USERNAME and PAY_ADVANTAGE_PASSWORD to your .env file")
            print("2. Ensure XERO configuration is set up in your .env file")
            print("3. Restart the application")
            
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            sys.exit(1)

if __name__ == '__main__':
    run_migrations()