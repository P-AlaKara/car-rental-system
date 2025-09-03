from datetime import datetime
from app import db


class VehicleReturn(db.Model):
    """Vehicle Return model for tracking return checklist and details."""
    
    __tablename__ = 'vehicle_returns'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    
    # Checklist items
    bond_returned = db.Column(db.Boolean, default=False, nullable=False)
    all_payments_received = db.Column(db.Boolean, default=False, nullable=False)
    car_in_good_condition = db.Column(db.Boolean, default=False, nullable=False)
    fuel_tank_full = db.Column(db.Boolean, default=False, nullable=False)
    
    # Vehicle details at return
    odometer_reading = db.Column(db.Integer, nullable=False)
    fuel_level = db.Column(db.String(20))  # Full, 3/4, 1/2, 1/4, Empty
    
    # Damage assessment
    damage_noted = db.Column(db.Boolean, default=False)
    damage_description = db.Column(db.Text)
    damage_charges = db.Column(db.Float, default=0)
    
    # Additional charges
    fuel_charges = db.Column(db.Float, default=0)
    late_return_charges = db.Column(db.Float, default=0)
    other_charges = db.Column(db.Float, default=0)
    charges_description = db.Column(db.Text)
    
    # Return details
    return_notes = db.Column(db.Text)
    returned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Staff who processed return
    return_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref=db.backref('vehicle_return', uselist=False), lazy=True)
    processor = db.relationship('User', foreign_keys=[returned_by], backref='processed_returns')
    
    def __repr__(self):
        return f'<VehicleReturn for Booking {self.booking_id}>'
    
    def calculate_total_charges(self):
        """Calculate total additional charges."""
        return (self.damage_charges or 0) + (self.fuel_charges or 0) + \
               (self.late_return_charges or 0) + (self.other_charges or 0)
    
    def is_checklist_complete(self):
        """Check if all checklist items are completed."""
        return all([
            self.bond_returned,
            self.all_payments_received,
            self.car_in_good_condition,
            self.fuel_tank_full
        ])
    
    def to_dict(self):
        """Convert return object to dictionary."""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'bond_returned': self.bond_returned,
            'all_payments_received': self.all_payments_received,
            'car_in_good_condition': self.car_in_good_condition,
            'fuel_tank_full': self.fuel_tank_full,
            'odometer_reading': self.odometer_reading,
            'fuel_level': self.fuel_level,
            'damage_noted': self.damage_noted,
            'damage_description': self.damage_description,
            'total_charges': self.calculate_total_charges(),
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'returned_by': self.returned_by
        }