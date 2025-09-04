from datetime import datetime
from enum import Enum
from app import db


class CarCategory(Enum):
    ECONOMY = 'economy'
    COMPACT = 'compact'
    MIDSIZE = 'midsize'
    FULLSIZE = 'fullsize'
    LUXURY = 'luxury'
    SUV = 'suv'
    MINIVAN = 'minivan'
    CONVERTIBLE = 'convertible'
    SPORTS = 'sports'
    ELECTRIC = 'electric'


class CarStatus(Enum):
    AVAILABLE = 'available'
    BOOKED = 'booked'
    MAINTENANCE = 'maintenance'
    OUT_OF_SERVICE = 'out_of_service'


class Car(db.Model):
    """Car model for fleet management."""
    
    __tablename__ = 'cars'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    vin = db.Column(db.String(50), unique=True, nullable=False)
    
    # Category and type
    category = db.Column(db.Enum(CarCategory), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    transmission = db.Column(db.String(20), default='Automatic')  # Automatic, Manual
    fuel_type = db.Column(db.String(20), default='Gasoline')  # Gasoline, Diesel, Electric, Hybrid
    
    # Rental information
    daily_rate = db.Column(db.Float, nullable=False)
    weekly_rate = db.Column(db.Float)
    monthly_rate = db.Column(db.Float)
    
    # Status and availability
    status = db.Column(db.Enum(CarStatus), default=CarStatus.AVAILABLE, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Features
    features = db.Column(db.JSON)  # Store as JSON array: ['GPS', 'Bluetooth', 'Backup Camera']
    
    # Images
    main_image = db.Column(db.String(255))
    images = db.Column(db.JSON)  # Store multiple image URLs as JSON array
    # Documents (images or PDFs) related to the car
    documents = db.Column(db.JSON)  # [{"type":"registration","url":"/uploads/...","name":"...","mime":"..."}]
    
    # Vehicle details
    color = db.Column(db.String(30))
    mileage = db.Column(db.Integer, default=0)  # Current odometer reading
    agency = db.Column(db.String(100))  # Agency/Branch
    current_odometer = db.Column(db.Integer, default=0)  # Current odometer in km
    last_service_odometer = db.Column(db.Integer, default=0)  # Last service odometer in km
    service_threshold = db.Column(db.Integer, default=5000)  # Service threshold in km
    last_service_date = db.Column(db.Date)
    next_service_due = db.Column(db.Date)
    insurance_expiry = db.Column(db.Date)
    registration_expiry = db.Column(db.Date)
    
    # Location
    current_location = db.Column(db.String(255))
    home_location = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='car', lazy='dynamic')
    maintenance_records = db.relationship('Maintenance', backref='car', lazy='dynamic')
    
    def __repr__(self):
        return f'<Car {self.year} {self.make} {self.model}>'
    
    @property
    def full_name(self):
        """Return the car's full name."""
        return f"{self.year} {self.make} {self.model}"
    
    @property
    def is_available(self):
        """Check if car is available for booking."""
        return self.status == CarStatus.AVAILABLE and self.is_active
    
    def calculate_rental_cost(self, days):
        """Calculate rental cost based on number of days."""
        if days >= 30 and self.monthly_rate:
            months = days // 30
            remaining_days = days % 30
            return (months * self.monthly_rate) + (remaining_days * self.daily_rate)
        elif days >= 7 and self.weekly_rate:
            weeks = days // 7
            remaining_days = days % 7
            return (weeks * self.weekly_rate) + (remaining_days * self.daily_rate)
        else:
            return days * self.daily_rate
    
    @property
    def km_until_service(self):
        """Calculate kilometers remaining until next service."""
        if self.current_odometer and self.last_service_odometer and self.service_threshold:
            return (self.last_service_odometer + self.service_threshold) - self.current_odometer
        return None
    
    @property
    def service_status(self):
        """Get the service status of the vehicle."""
        km_remaining = self.km_until_service
        if km_remaining is None:
            return 'unknown'
        elif km_remaining < 0:
            return 'overdue'
        elif km_remaining <= 500:
            return 'due_soon'
        elif self.status == CarStatus.MAINTENANCE:
            return 'in_service'
        else:
            return 'healthy'
    
    def to_dict(self):
        """Convert car object to dictionary."""
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'full_name': self.full_name,
            'license_plate': self.license_plate,
            'category': self.category.value,
            'seats': self.seats,
            'transmission': self.transmission,
            'fuel_type': self.fuel_type,
            'daily_rate': self.daily_rate,
            'weekly_rate': self.weekly_rate,
            'monthly_rate': self.monthly_rate,
            'status': self.status.value,
            'is_available': self.is_available,
            'features': self.features or [],
            'main_image': self.main_image,
            'images': self.images or [],
            'documents': self.documents or [],
            'color': self.color,
            'mileage': self.mileage,
            'current_location': self.current_location
        }