#!/usr/bin/env python3
"""Test script to verify admin dashboard functionality."""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Car, Booking, Payment, Maintenance, Role
from app.models import CarCategory, CarStatus, BookingStatus, PaymentStatus, MaintenanceType, MaintenanceStatus, PaymentMethod
from datetime import datetime, timedelta
import random

def create_test_data():
    """Create test data for the admin dashboard."""
    app = create_app('default')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@aurora.com').first()
        if not admin:
            admin = User(
                email='admin@aurora.com',
                username='admin',
                first_name='Admin',
                last_name='User',
                role=Role.ADMIN,
                phone='+61 400 000 000'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user: admin@aurora.com / admin123")
        
        # Create test customers if they don't exist
        for i in range(1, 6):
            email = f'customer{i}@test.com'
            if not User.query.filter_by(email=email).first():
                customer = User(
                    email=email,
                    username=f'customer{i}',
                    first_name=f'Customer',
                    last_name=f'{i}',
                    role=Role.CUSTOMER,
                    phone=f'+61 400 000 {i:03d}'
                )
                customer.set_password('password123')
                db.session.add(customer)
                print(f"Created customer: {email}")
        
        # Create test cars if they don't exist
        if Car.query.count() < 10:
            car_data = [
                ('Toyota', 'Camry', 2023, 'ABC123', 'VIN123456789', CarCategory.MIDSIZE, 85.00),
                ('Honda', 'Civic', 2023, 'XYZ789', 'VIN987654321', CarCategory.COMPACT, 75.00),
                ('Tesla', 'Model 3', 2024, 'EV001', 'VINEV123456', CarCategory.ELECTRIC, 120.00),
                ('BMW', '3 Series', 2023, 'LUX100', 'VINBMW12345', CarCategory.LUXURY, 150.00),
                ('Toyota', 'RAV4', 2023, 'SUV200', 'VINSUV12345', CarCategory.SUV, 95.00),
                ('Mazda', 'CX-5', 2022, 'MAZ300', 'VINMAZ12345', CarCategory.SUV, 90.00),
                ('Ford', 'Mustang', 2023, 'SPT400', 'VINSPT12345', CarCategory.SPORTS, 180.00),
                ('Volkswagen', 'Golf', 2023, 'VW500', 'VINVW123456', CarCategory.COMPACT, 70.00),
                ('Mercedes', 'C-Class', 2024, 'MRC600', 'VINMRC12345', CarCategory.LUXURY, 160.00),
                ('Nissan', 'Altima', 2023, 'NSN700', 'VINNSN12345', CarCategory.MIDSIZE, 80.00)
            ]
            
            for make, model, year, plate, vin, category, rate in car_data:
                if not Car.query.filter_by(license_plate=plate).first():
                    car = Car(
                        make=make,
                        model=model,
                        year=year,
                        license_plate=plate,
                        vin=vin,
                        category=category,
                        seats=5,
                        transmission='Automatic',
                        fuel_type='Gasoline' if category != CarCategory.ELECTRIC else 'Electric',
                        daily_rate=rate,
                        weekly_rate=rate * 6.5,
                        monthly_rate=rate * 25,
                        color='Silver',
                        agency='Melbourne CBD',
                        current_odometer=random.randint(5000, 50000),
                        last_service_odometer=random.randint(1000, 4000),
                        service_threshold=5000,
                        status=random.choice([CarStatus.AVAILABLE, CarStatus.AVAILABLE, CarStatus.BOOKED]),
                        current_location='123 Collins St, Melbourne',
                        features=['GPS', 'Bluetooth', 'Air Conditioning', 'USB Charging']
                    )
                    db.session.add(car)
                    print(f"Created car: {year} {make} {model}")
        
        # Create test bookings if they don't exist
        if Booking.query.count() < 10:
            customers = User.query.filter_by(role=Role.CUSTOMER).all()
            cars = Car.query.all()
            
            for i in range(10):
                booking = Booking(
                    customer_id=random.choice(customers).id,
                    car_id=random.choice(cars).id,
                    pickup_date=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                    return_date=datetime.utcnow() + timedelta(days=random.randint(31, 60)),
                    pickup_location='Melbourne Airport',
                    return_location='Melbourne CBD',
                    daily_rate=85.00,
                    total_days=random.randint(3, 14),
                    subtotal=85.00 * random.randint(3, 14),
                    total_amount=85.00 * random.randint(3, 14) * 1.1,  # Add 10% tax
                    status=random.choice(list(BookingStatus))
                )
                booking.generate_booking_number()
                db.session.add(booking)
                print(f"Created booking: {booking.booking_number}")
        
        # Create test payments
        bookings = Booking.query.all()
        for booking in bookings[:5]:  # Create payments for first 5 bookings
            if not Payment.query.filter_by(booking_id=booking.id).first():
                payment = Payment(
                    booking_id=booking.id,
                    user_id=booking.customer_id,
                    amount=booking.total_amount,
                    payment_method=PaymentMethod.CREDIT_CARD,
                    status=PaymentStatus.COMPLETED,
                    transaction_id=f'TXN{booking.id:06d}'
                )
                db.session.add(payment)
                print(f"Created payment for booking: {booking.booking_number}")
        
        # Create test maintenance records
        cars = Car.query.all()
        for car in cars[:3]:  # Create maintenance for first 3 cars
            if not Maintenance.query.filter_by(car_id=car.id).first():
                maintenance = Maintenance(
                    car_id=car.id,
                    type=random.choice([MaintenanceType.OIL_CHANGE, MaintenanceType.TIRE_ROTATION, MaintenanceType.INSPECTION]),
                    service_date=datetime.utcnow().date() + timedelta(days=random.randint(1, 30)),
                    description='Scheduled maintenance service',
                    status=MaintenanceStatus.SCHEDULED,
                    total_cost=random.randint(100, 500)
                )
                db.session.add(maintenance)
                print(f"Created maintenance for car: {car.full_name}")
        
        # Commit all changes
        db.session.commit()
        print("\nTest data created successfully!")
        print("\nAdmin Dashboard Access:")
        print("URL: http://localhost:5000/admin")
        print("Login: admin@aurora.com / admin123")
        print("\nThe admin dashboard includes:")
        print("- Dashboard with statistics and charts")
        print("- Bookings management with filtering and actions")
        print("- Fleet management for vehicles")
        print("- User management")
        print("- Payment history")
        print("- Maintenance tracking")

if __name__ == '__main__':
    create_test_data()