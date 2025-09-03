from datetime import datetime
from enum import Enum
from app import db


class MaintenanceType(Enum):
    ROUTINE = 'routine'
    REPAIR = 'repair'
    INSPECTION = 'inspection'
    ACCIDENT = 'accident'
    CLEANING = 'cleaning'
    OIL_CHANGE = 'oil_change'
    TIRE_ROTATION = 'tire_rotation'
    BRAKE_SERVICE = 'brake_service'
    BATTERY_REPLACEMENT = 'battery_replacement'
    TRANSMISSION_SERVICE = 'transmission_service'
    OTHER = 'other'


class MaintenanceStatus(Enum):
    SCHEDULED = 'scheduled'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class Maintenance(db.Model):
    """Maintenance model for vehicle service records."""
    
    __tablename__ = 'maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    
    # Maintenance details
    type = db.Column(db.Enum(MaintenanceType), nullable=False)
    status = db.Column(db.Enum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED)
    
    # Service information
    service_date = db.Column(db.Date, nullable=False)
    completion_date = db.Column(db.Date)
    mileage_at_service = db.Column(db.Integer)
    
    # Description and work performed
    description = db.Column(db.Text, nullable=False)
    work_performed = db.Column(db.Text)
    parts_replaced = db.Column(db.JSON)  # JSON array of parts
    
    # Service provider
    service_provider = db.Column(db.String(100))
    technician_name = db.Column(db.String(100))
    
    # Cost
    labor_cost = db.Column(db.Float, default=0)
    parts_cost = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    
    # Invoice and warranty
    invoice_number = db.Column(db.String(50))
    warranty_months = db.Column(db.Integer, default=0)
    
    # Next service
    next_service_date = db.Column(db.Date)
    next_service_mileage = db.Column(db.Integer)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Maintenance {self.type.value} for Car {self.car_id}>'
    
    def calculate_total_cost(self):
        """Calculate total maintenance cost."""
        self.total_cost = self.labor_cost + self.parts_cost
        return self.total_cost
    
    def to_dict(self):
        """Convert maintenance object to dictionary."""
        return {
            'id': self.id,
            'car_id': self.car_id,
            'car_name': self.car.full_name if self.car else None,
            'type': self.type.value,
            'status': self.status.value,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'description': self.description,
            'total_cost': self.total_cost,
            'service_provider': self.service_provider,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }