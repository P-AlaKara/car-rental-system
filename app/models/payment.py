from datetime import datetime
from enum import Enum
from app import db


class PaymentStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    CANCELLED = 'cancelled'


class PaymentMethod(Enum):
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    PAYPAL = 'paypal'
    STRIPE = 'stripe'
    CASH = 'cash'
    BANK_TRANSFER = 'bank_transfer'
    DIRECT_DEBIT = 'direct_debit'


class Payment(db.Model):
    """Payment model for transaction management."""
    
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    
    # Foreign keys
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Payment details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Payment gateway information
    gateway = db.Column(db.String(50))  # 'stripe', 'paypal', etc.
    gateway_transaction_id = db.Column(db.String(255))
    gateway_response = db.Column(db.JSON)  # Store full gateway response
    
    # Card information (encrypted/tokenized)
    card_last_four = db.Column(db.String(4))
    card_brand = db.Column(db.String(20))  # Visa, Mastercard, etc.
    
    # Billing information
    billing_name = db.Column(db.String(100))
    billing_email = db.Column(db.String(120))
    billing_phone = db.Column(db.String(20))
    billing_address = db.Column(db.Text)
    billing_city = db.Column(db.String(50))
    billing_state = db.Column(db.String(50))
    billing_zip = db.Column(db.String(10))
    billing_country = db.Column(db.String(50))
    
    # Refund information
    refund_amount = db.Column(db.Float, default=0)
    refund_reason = db.Column(db.Text)
    refunded_at = db.Column(db.DateTime)
    
    # Additional information
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'
    
    @property
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == PaymentStatus.COMPLETED
    
    @property
    def can_refund(self):
        """Check if payment can be refunded."""
        return self.status == PaymentStatus.COMPLETED and self.refund_amount < self.amount
    
    def generate_transaction_id(self):
        """Generate a unique transaction ID."""
        import random
        import string
        prefix = 'TXN'
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.transaction_id = f"{prefix}{timestamp}{random_str}"
    
    def process_refund(self, amount, reason):
        """Process a refund for this payment."""
        if not self.can_refund:
            raise ValueError("Payment cannot be refunded")
        
        if amount > (self.amount - self.refund_amount):
            raise ValueError("Refund amount exceeds available balance")
        
        self.refund_amount += amount
        self.refund_reason = reason
        self.refunded_at = datetime.utcnow()
        
        if self.refund_amount >= self.amount:
            self.status = PaymentStatus.REFUNDED
    
    def to_dict(self):
        """Convert payment object to dictionary."""
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'booking_id': self.booking_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method.value,
            'status': self.status.value,
            'card_last_four': self.card_last_four,
            'card_brand': self.card_brand,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }