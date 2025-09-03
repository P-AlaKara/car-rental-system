from datetime import datetime, timedelta
from app import db


class XeroToken(db.Model):
    """Model for storing Xero OAuth2 tokens."""
    
    __tablename__ = 'xero_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Token data
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    token_type = db.Column(db.String(50), default='Bearer')
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Xero specific data
    tenant_id = db.Column(db.String(255))
    tenant_name = db.Column(db.String(255))
    tenant_type = db.Column(db.String(50))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<XeroToken {self.id}>'
    
    @property
    def is_expired(self):
        """Check if the access token has expired."""
        if self.expires_at:
            # Add a 1-minute buffer to account for clock differences
            return datetime.utcnow() >= (self.expires_at - timedelta(minutes=1))
        return True
    
    @property
    def needs_refresh(self):
        """Check if the token needs to be refreshed (5 minutes before expiry)."""
        if self.expires_at:
            return datetime.utcnow() >= (self.expires_at - timedelta(minutes=5))
        return True
    
    def update_tokens(self, token_data):
        """Update token data from Xero response."""
        self.access_token = token_data.get('access_token')
        self.refresh_token = token_data.get('refresh_token', self.refresh_token)
        self.token_type = token_data.get('token_type', 'Bearer')
        
        # Calculate expiry time
        expires_in = token_data.get('expires_in', 1800)  # Default to 30 minutes
        self.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        self.updated_at = datetime.utcnow()
        
    def to_dict(self):
        """Convert token object to dictionary."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'tenant_name': self.tenant_name,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired,
            'needs_refresh': self.needs_refresh,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }