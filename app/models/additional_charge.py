from datetime import datetime
from enum import Enum
from app import db


class ChargeType(Enum):
    """Types of additional charges."""
    DAMAGE = 'damage'
    FUEL = 'fuel'
    LATE_RETURN = 'late_return'
    CLEANING = 'cleaning'
    TRAFFIC_FINE = 'traffic_fine'
    TOLL = 'toll'
    EXCESS_MILEAGE = 'excess_mileage'
    OTHER = 'other'


class ChargeStatus(Enum):
    """Status of additional charges."""
    PENDING = 'pending'
    APPROVED = 'approved'
    DISPUTED = 'disputed'
    PAID = 'paid'
    WAIVED = 'waived'
    REFUNDED = 'refunded'


class AdditionalCharge(db.Model):
    """Model for tracking additional charges during or after rental."""
    
    __tablename__ = 'additional_charges'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    
    # Charge details
    charge_type = db.Column(db.Enum(ChargeType), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    # Status tracking
    status = db.Column(db.Enum(ChargeStatus), default=ChargeStatus.PENDING, nullable=False)
    
    # When the charge was incurred
    incurred_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Supporting documentation
    evidence_file_path = db.Column(db.String(255))  # Path to photo or document
    notes = db.Column(db.Text)
    
    # Processing details
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_date = db.Column(db.DateTime)
    
    # Payment tracking
    paid_date = db.Column(db.DateTime)
    payment_reference = db.Column(db.String(100))
    
    # If charge is disputed
    dispute_reason = db.Column(db.Text)
    dispute_date = db.Column(db.DateTime)
    dispute_resolved_date = db.Column(db.DateTime)
    dispute_resolution = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Created by (staff member who added the charge)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    booking = db.relationship('Booking', backref='additional_charge_items', lazy=True)
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_charges')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_charges')
    
    def __repr__(self):
        return f'<AdditionalCharge {self.charge_type.value}: ${self.amount} for Booking {self.booking_id}>'
    
    def to_dict(self):
        """Convert charge object to dictionary."""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'charge_type': self.charge_type.value if self.charge_type else None,
            'description': self.description,
            'amount': self.amount,
            'status': self.status.value if self.status else None,
            'incurred_date': self.incurred_date.isoformat() if self.incurred_date else None,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_pending_charges_total(cls, booking_id):
        """Get total amount of pending charges for a booking."""
        result = db.session.query(db.func.sum(cls.amount)).filter_by(
            booking_id=booking_id,
            status=ChargeStatus.PENDING
        ).scalar()
        return result or 0
    
    @classmethod
    def get_approved_charges_total(cls, booking_id):
        """Get total amount of approved charges for a booking."""
        result = db.session.query(db.func.sum(cls.amount)).filter_by(
            booking_id=booking_id,
            status=ChargeStatus.APPROVED
        ).scalar()
        return result or 0
    
    def approve(self, user_id):
        """Approve this charge."""
        self.status = ChargeStatus.APPROVED
        self.approved_by = user_id
        self.approved_date = datetime.utcnow()
    
    def dispute(self, reason):
        """Mark this charge as disputed."""
        self.status = ChargeStatus.DISPUTED
        self.dispute_reason = reason
        self.dispute_date = datetime.utcnow()
    
    def mark_paid(self, payment_reference=None):
        """Mark this charge as paid."""
        self.status = ChargeStatus.PAID
        self.paid_date = datetime.utcnow()
        self.payment_reference = payment_reference
    
    def waive(self, reason=None):
        """Waive this charge."""
        self.status = ChargeStatus.WAIVED
        if reason:
            self.notes = (self.notes or '') + f'\nWaived: {reason}'