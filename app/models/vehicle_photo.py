from datetime import datetime
from enum import Enum
from app import db


class PhotoType(Enum):
    PICKUP = 'pickup'
    RETURN = 'return'
    DAMAGE = 'damage'


class VehiclePhoto(db.Model):
    """Vehicle Photo model for storing condition photos during pickup/return."""
    
    __tablename__ = 'vehicle_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    
    # Photo details
    photo_url = db.Column(db.String(500), nullable=False)
    photo_type = db.Column(db.Enum(PhotoType), nullable=False)
    caption = db.Column(db.String(255))
    
    # Photo metadata
    angle = db.Column(db.String(50))  # front, back, left, right, interior, damage
    
    # Upload details
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref='photos', lazy=True)
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f'<VehiclePhoto {self.id} for Booking {self.booking_id}>'
    
    def to_dict(self):
        """Convert photo object to dictionary."""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'photo_url': self.photo_url,
            'photo_type': self.photo_type.value,
            'caption': self.caption,
            'angle': self.angle,
            'uploaded_by': self.uploader.full_name if self.uploader else None,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }