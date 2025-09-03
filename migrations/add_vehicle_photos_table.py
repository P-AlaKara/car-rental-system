"""
Migration script to add vehicle_photos table for storing vehicle condition photos
"""

import sqlite3
from datetime import datetime

def upgrade():
    """Create the vehicle_photos table"""
    conn = sqlite3.connect('instance/car_rental.db')
    cursor = conn.cursor()
    
    # Create vehicle_photos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            photo_url VARCHAR(500) NOT NULL,
            photo_type VARCHAR(20) NOT NULL,
            caption VARCHAR(255),
            angle VARCHAR(50),
            uploaded_by INTEGER NOT NULL,
            upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
    ''')
    
    # Create index on booking_id for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_vehicle_photos_booking_id 
        ON vehicle_photos(booking_id)
    ''')
    
    # Create index on photo_type for filtering
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_vehicle_photos_type 
        ON vehicle_photos(photo_type)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Successfully created vehicle_photos table")

def downgrade():
    """Drop the vehicle_photos table"""
    conn = sqlite3.connect('instance/car_rental.db')
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS vehicle_photos')
    
    conn.commit()
    conn.close()
    print("✅ Successfully dropped vehicle_photos table")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()