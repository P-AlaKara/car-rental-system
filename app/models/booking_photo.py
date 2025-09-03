from datetime import datetime
from app import db


class BookingPhoto(db.Model):
    """Model for storing photos of vehicles at pickup and return."""
    
    __tablename__ = 'booking_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    photo_type = db.Column(db.String(50), nullable=False)  # 'pickup' or 'return'
    photo_url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    booking = db.relationship('Booking', backref='booking_photos', lazy=True)
    uploader = db.relationship('User', backref='uploaded_photos', lazy=True)
    
    def __repr__(self):
        return f'<BookingPhoto {self.id} - {self.photo_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'photo_type': self.photo_type,
            'photo_url': self.photo_url,
            'description': self.description,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'uploaded_by': self.uploaded_by
        }