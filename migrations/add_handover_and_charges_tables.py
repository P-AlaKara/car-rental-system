"""
Migration script to add vehicle_handovers, handover_photos, and additional_charges tables.
Run this script to update your database schema.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def run_migration():
    """Run the migration to add new tables."""
    app = create_app()
    
    with app.app_context():
        # Create vehicle_handovers table
        create_handovers_table = """
        CREATE TABLE IF NOT EXISTS vehicle_handovers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL UNIQUE,
            license_verified BOOLEAN DEFAULT FALSE NOT NULL,
            license_number VARCHAR(50),
            license_expiry_date DATE,
            contract_signed BOOLEAN DEFAULT FALSE,
            contract_file_path VARCHAR(255),
            contract_signed_date DATETIME,
            odometer_reading INTEGER NOT NULL,
            fuel_level VARCHAR(20),
            vehicle_condition_notes TEXT,
            direct_debit_setup JSON,
            handover_completed BOOLEAN DEFAULT FALSE,
            handover_by INTEGER NOT NULL,
            handover_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            handover_notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (handover_by) REFERENCES users(id)
        );
        """
        
        # Create handover_photos table
        create_photos_table = """
        CREATE TABLE IF NOT EXISTS handover_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            handover_id INTEGER NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            file_name VARCHAR(100) NOT NULL,
            description VARCHAR(255),
            photo_type VARCHAR(50),
            uploaded_by INTEGER NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (handover_id) REFERENCES vehicle_handovers(id) ON DELETE CASCADE,
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        );
        """
        
        # Create additional_charges table
        create_charges_table = """
        CREATE TABLE IF NOT EXISTS additional_charges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            charge_type VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            amount FLOAT NOT NULL,
            status VARCHAR(50) DEFAULT 'pending' NOT NULL,
            incurred_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            evidence_file_path VARCHAR(255),
            notes TEXT,
            approved_by INTEGER,
            approved_date DATETIME,
            paid_date DATETIME,
            payment_reference VARCHAR(100),
            dispute_reason TEXT,
            dispute_date DATETIME,
            dispute_resolved_date DATETIME,
            dispute_resolution TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (approved_by) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        """
        
        # Create indexes for better performance
        create_indexes = """
        CREATE INDEX IF NOT EXISTS idx_vehicle_handovers_booking_id ON vehicle_handovers(booking_id);
        CREATE INDEX IF NOT EXISTS idx_handover_photos_handover_id ON handover_photos(handover_id);
        CREATE INDEX IF NOT EXISTS idx_additional_charges_booking_id ON additional_charges(booking_id);
        CREATE INDEX IF NOT EXISTS idx_additional_charges_status ON additional_charges(status);
        """
        
        try:
            # Execute the SQL statements
            db.session.execute(text(create_handovers_table))
            db.session.execute(text(create_photos_table))
            db.session.execute(text(create_charges_table))
            
            # Create indexes
            for index_sql in create_indexes.strip().split(';'):
                if index_sql.strip():
                    db.session.execute(text(index_sql.strip()))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            print("   - Created vehicle_handovers table")
            print("   - Created handover_photos table")
            print("   - Created additional_charges table")
            print("   - Created indexes for performance")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    run_migration()