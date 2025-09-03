"""
Migration script to add vehicle_returns table for tracking vehicle return checklists
"""

import sqlite3
from datetime import datetime

def upgrade():
    """Create the vehicle_returns table"""
    conn = sqlite3.connect('instance/car_rental.db')
    cursor = conn.cursor()
    
    # Create vehicle_returns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL UNIQUE,
            bond_returned BOOLEAN DEFAULT 0 NOT NULL,
            all_payments_received BOOLEAN DEFAULT 0 NOT NULL,
            car_in_good_condition BOOLEAN DEFAULT 0 NOT NULL,
            fuel_tank_full BOOLEAN DEFAULT 0 NOT NULL,
            odometer_reading INTEGER NOT NULL,
            fuel_level VARCHAR(20),
            damage_noted BOOLEAN DEFAULT 0,
            damage_description TEXT,
            damage_charges REAL DEFAULT 0,
            fuel_charges REAL DEFAULT 0,
            late_return_charges REAL DEFAULT 0,
            other_charges REAL DEFAULT 0,
            charges_description TEXT,
            return_notes TEXT,
            returned_by INTEGER NOT NULL,
            return_date DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (returned_by) REFERENCES users(id)
        )
    ''')
    
    # Create index on booking_id for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_vehicle_returns_booking_id 
        ON vehicle_returns(booking_id)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Successfully created vehicle_returns table")

def downgrade():
    """Drop the vehicle_returns table"""
    conn = sqlite3.connect('instance/car_rental.db')
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS vehicle_returns')
    
    conn.commit()
    conn.close()
    print("✅ Successfully dropped vehicle_returns table")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()