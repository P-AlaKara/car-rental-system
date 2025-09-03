from datetime import datetime
from app import db


class VehicleHandover(db.Model):
    """Vehicle Handover model for tracking handover details and photos."""
    
    __tablename__ = 'vehicle_handovers'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    
    # License verification
    license_verified = db.Column(db.Boolean, default=False, nullable=False)
    license_number = db.Column(db.String(50))
    license_expiry_date = db.Column(db.Date)
    
    # Contract details
    contract_signed = db.Column(db.Boolean, default=False)
    contract_file_path = db.Column(db.String(255))
    contract_signed_date = db.Column(db.DateTime)
    
    # Vehicle condition at handover
    odometer_reading = db.Column(db.Integer, nullable=False)
    fuel_level = db.Column(db.String(20))  # Full, 3/4, 1/2, 1/4, Empty
    vehicle_condition_notes = db.Column(db.Text)
    
    # Direct debit details (stored as JSON for flexibility)
    direct_debit_setup = db.Column(db.JSON)
    
    # Handover details
    handover_completed = db.Column(db.Boolean, default=False)
    handover_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Staff who processed handover
    handover_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    handover_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref=db.backref('vehicle_handover', uselist=False), lazy=True)
    processor = db.relationship('User', foreign_keys=[handover_by], backref='processed_handovers')
    photos = db.relationship('HandoverPhoto', backref='handover', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VehicleHandover for Booking {self.booking_id}>'
    
    def to_dict(self):
        """Convert handover object to dictionary."""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'license_verified': self.license_verified,
            'contract_signed': self.contract_signed,
            'odometer_reading': self.odometer_reading,
            'fuel_level': self.fuel_level,
            'handover_completed': self.handover_completed,
            'handover_date': self.handover_date.isoformat() if self.handover_date else None,
            'handover_by': self.handover_by,
            'photos_count': len(self.photos) if self.photos else 0
        }


class HandoverPhoto(db.Model):
    """Model for storing vehicle photos taken during handover."""
    
    __tablename__ = 'handover_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    handover_id = db.Column(db.Integer, db.ForeignKey('vehicle_handovers.id'), nullable=False)
    
    # Photo details
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))  # e.g., "Front view", "Left side damage", etc.
    photo_type = db.Column(db.String(50))  # e.g., "exterior", "interior", "damage", "document"
    
    # Metadata
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_photos')
    
    def __repr__(self):
        return f'<HandoverPhoto {self.file_name} for Handover {self.handover_id}>'
    
    def to_dict(self):
        """Convert photo object to dictionary."""
        return {
            'id': self.id,
            'handover_id': self.handover_id,
            'file_name': self.file_name,
            'url': f'/uploads/handover/{self.file_name}',  # Adjust based on your file serving setup
            'description': self.description,
            'photo_type': self.photo_type,
            'timestamp': self.uploaded_at.isoformat() if self.uploaded_at else None
        }