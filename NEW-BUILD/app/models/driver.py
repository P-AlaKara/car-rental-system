from datetime import datetime
from enum import Enum
from app import db


class DriverStatus(Enum):
    AVAILABLE = 'available'
    ON_DUTY = 'on_duty'
    OFF_DUTY = 'off_duty'
    ON_LEAVE = 'on_leave'
    SUSPENDED = 'suspended'


class Driver(db.Model):
    """Driver model for driver management."""
    
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Driver information
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_class = db.Column(db.String(10), nullable=False)  # e.g., 'Class B', 'CDL'
    license_expiry = db.Column(db.Date, nullable=False)
    license_state = db.Column(db.String(50))
    
    # Employment details
    hire_date = db.Column(db.Date, nullable=False)
    termination_date = db.Column(db.Date)
    hourly_rate = db.Column(db.Float)
    commission_rate = db.Column(db.Float, default=0)  # Percentage of booking amount
    
    # Status and availability
    status = db.Column(db.Enum(DriverStatus), default=DriverStatus.AVAILABLE, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Performance metrics
    total_trips = db.Column(db.Integer, default=0)
    total_hours = db.Column(db.Float, default=0)
    rating = db.Column(db.Float, default=5.0)  # Average rating out of 5
    total_ratings = db.Column(db.Integer, default=0)
    
    # Emergency contact
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(50))
    
    # Medical and background
    medical_cert_expiry = db.Column(db.Date)
    background_check_date = db.Column(db.Date)
    drug_test_date = db.Column(db.Date)
    
    # Vehicle preferences
    preferred_car_types = db.Column(db.JSON)  # JSON array of car categories
    max_daily_hours = db.Column(db.Integer, default=8)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='driver', lazy='dynamic')
    
    def __repr__(self):
        return f'<Driver {self.employee_id}>'
    
    @property
    def is_available(self):
        """Check if driver is available for assignment."""
        return self.status == DriverStatus.AVAILABLE and self.is_active
    
    @property
    def full_name(self):
        """Get driver's full name from user relationship."""
        return self.user.full_name if self.user else None
    
    def update_rating(self, new_rating):
        """Update driver's average rating."""
        if self.total_ratings == 0:
            self.rating = new_rating
        else:
            total_score = self.rating * self.total_ratings
            self.rating = (total_score + new_rating) / (self.total_ratings + 1)
        self.total_ratings += 1
    
    def calculate_commission(self, booking_amount):
        """Calculate commission for a booking."""
        if self.commission_rate:
            return booking_amount * (self.commission_rate / 100)
        return 0
    
    def generate_employee_id(self):
        """Generate a unique employee ID."""
        import random
        prefix = 'DRV'
        year = datetime.utcnow().strftime('%Y')
        random_num = random.randint(1000, 9999)
        self.employee_id = f"{prefix}{year}{random_num}"
    
    def to_dict(self):
        """Convert driver object to dictionary."""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'full_name': self.full_name,
            'email': self.user.email if self.user else None,
            'phone': self.user.phone if self.user else None,
            'license_number': self.license_number,
            'license_class': self.license_class,
            'license_expiry': self.license_expiry.isoformat() if self.license_expiry else None,
            'status': self.status.value,
            'is_active': self.is_active,
            'rating': self.rating,
            'total_trips': self.total_trips,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None
        }