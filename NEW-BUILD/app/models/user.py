from datetime import datetime
from enum import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class Role(Enum):
    CUSTOMER = 'customer'
    DRIVER = 'driver'
    ADMIN = 'admin'
    MANAGER = 'manager'


class User(UserMixin, db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    country = db.Column(db.String(50), default='USA')
    
    # Role and permissions
    role = db.Column(db.Enum(Role), default=Role.CUSTOMER, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Additional fields
    profile_picture = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    license_number = db.Column(db.String(50))
    license_expiry = db.Column(db.Date)
    
    # Relationships
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic', 
                              foreign_keys='Booking.customer_id')
    driver_profile = db.relationship('Driver', backref='user', uselist=False)
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == Role.ADMIN
    
    @property
    def is_manager(self):
        """Check if user has manager role."""
        return self.role in [Role.ADMIN, Role.MANAGER]
    
    @property
    def is_driver(self):
        """Check if user has driver role."""
        return self.role == Role.DRIVER
    
    @property
    def is_customer(self):
        """Check if user has customer role."""
        return self.role == Role.CUSTOMER
    
    def can_access_dashboard(self):
        """Check if user can access admin dashboard."""
        return self.role in [Role.ADMIN, Role.MANAGER]
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role.value,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'profile_picture': self.profile_picture
        }


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))