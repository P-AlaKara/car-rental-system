from datetime import datetime
from app import db


class PayAdvantageCustomer(db.Model):
    """Model for storing PayAdvantage customer codes."""
    
    __tablename__ = 'pay_advantage_customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_code = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='pay_advantage_customer', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<PayAdvantageCustomer {self.customer_code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'customer_code': self.customer_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DirectDebitSchedule(db.Model):
    """Model for storing direct debit schedules."""
    
    __tablename__ = 'direct_debit_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    schedule_id = db.Column(db.String(100), nullable=False, unique=True)
    customer_code = db.Column(db.String(100))
    description = db.Column(db.Text)
    upfront_amount = db.Column(db.Float)
    upfront_date = db.Column(db.Date)
    recurring_amount = db.Column(db.Float)
    recurring_start_date = db.Column(db.Date)
    frequency = db.Column(db.String(50))  # weekly, fortnightly, monthly
    end_condition_amount = db.Column(db.Float)
    status = db.Column(db.String(50))
    authorization_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref='direct_debit_schedule', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<DirectDebitSchedule {self.schedule_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'schedule_id': self.schedule_id,
            'customer_code': self.customer_code,
            'description': self.description,
            'upfront_amount': self.upfront_amount,
            'upfront_date': self.upfront_date.isoformat() if self.upfront_date else None,
            'recurring_amount': self.recurring_amount,
            'recurring_start_date': self.recurring_start_date.isoformat() if self.recurring_start_date else None,
            'frequency': self.frequency,
            'end_condition_amount': self.end_condition_amount,
            'status': self.status,
            'authorization_url': self.authorization_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }