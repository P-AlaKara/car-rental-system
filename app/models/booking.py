from datetime import datetime
from enum import Enum
from app import db


class BookingStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'


class Booking(db.Model):
    """Booking model for car rental reservations."""
    
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    
    # Booking dates and times
    pickup_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    actual_pickup_date = db.Column(db.DateTime)
    actual_return_date = db.Column(db.DateTime)
    
    # Locations
    pickup_location = db.Column(db.String(255), nullable=False)
    return_location = db.Column(db.String(255), nullable=False)
    
    # Pricing
    daily_rate = db.Column(db.Float, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    additional_charges = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, default=0)
    
    # Status
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # Additional options
    with_driver = db.Column(db.Boolean, default=False)
    insurance_opted = db.Column(db.Boolean, default=False)
    gps_opted = db.Column(db.Boolean, default=False)
    child_seat_opted = db.Column(db.Boolean, default=False)
    additional_driver = db.Column(db.Boolean, default=False)
    
    # Notes and special requests
    customer_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    special_requests = db.Column(db.Text)
    
    # Cancellation
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    cancellation_fee = db.Column(db.Float, default=0)
    
    # Handover and Return fields
    license_verified = db.Column(db.Boolean, default=False)
    license_verified_at = db.Column(db.DateTime)
    contract_signed_url = db.Column(db.Text)
    contract_signed_at = db.Column(db.DateTime)
    pickup_odometer = db.Column(db.Integer)
    return_odometer = db.Column(db.Integer)
    handover_completed_at = db.Column(db.DateTime)
    handover_completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    return_completed_at = db.Column(db.DateTime)
    return_completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    direct_debit_schedule_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='booking', lazy='dynamic')
    
    def __repr__(self):
        return f'<Booking {self.booking_number}>'
    
    @property
    def is_active(self):
        """Check if booking is currently active."""
        return self.status in [BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]
    
    @property
    def can_cancel(self):
        """Check if booking can be cancelled."""
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]
    
    @property
    def is_past_due(self):
        """Check if booking return date has passed."""
        if self.status == BookingStatus.IN_PROGRESS and self.return_date:
            return datetime.utcnow() > self.return_date
        return False
    
    def calculate_late_fees(self):
        """Calculate late fees if applicable."""
        if self.is_past_due and self.actual_return_date:
            days_late = (self.actual_return_date - self.return_date).days
            if days_late > 0:
                return days_late * self.daily_rate * 1.5  # 150% of daily rate for late fees
        return 0
    
    def generate_booking_number(self):
        """Generate a unique booking number."""
        import random
        import string
        prefix = 'BK'
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.booking_number = f"{prefix}{timestamp}{random_str}"
    
    def to_dict(self):
        """Convert booking object to dictionary."""
        return {
            'id': self.id,
            'booking_number': self.booking_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'car_id': self.car_id,
            'car_name': self.car.full_name if self.car else None,
            'pickup_date': self.pickup_date.isoformat() if self.pickup_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'pickup_location': self.pickup_location,
            'return_location': self.return_location,
            'total_days': self.total_days,
            'total_amount': self.total_amount,
            'status': self.status.value,
            'with_driver': self.with_driver,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }