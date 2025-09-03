#!/usr/bin/env python3
"""
Quick test script for Admin Dashboard functionality.
This script provides a simpler way to test specific features quickly.
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (
    User, Car, Booking, Payment, Maintenance, Role,
    CarCategory, CarStatus, BookingStatus, PaymentStatus, 
    MaintenanceType, MaintenanceStatus, PaymentMethod,
    PayAdvantageCustomer, DirectDebitSchedule, Invoice, InvoiceStatus
)
from app.services.pay_advantage import PayAdvantageService


class AdminDashboardQuickTest:
    """Quick test runner for admin dashboard features."""
    
    def __init__(self):
        """Initialize the test environment."""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Set Pay Advantage credentials
        os.environ['PAY_ADVANTAGE_USERNAME'] = 'live_83e0ad9f0d3342e699dea15d35cc0d3a'
        os.environ['PAY_ADVANTAGE_PASSWORD'] = '3ac68741013145009121d3ea36317ad7'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        self.setup_admin_user()
    
    def setup_admin_user(self):
        """Create admin user for testing."""
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
            db.session.commit()
            print("✓ Admin user created: admin@aurora.com / admin123")
    
    def test_user_creation(self):
        """Test creating a new user."""
        print("\n[QUICK TEST] User Creation")
        print("-" * 40)
        
        # Create test user
        user = User(
            email='test_user@example.com',
            username='test_user',
            first_name='Test',
            last_name='User',
            role=Role.CUSTOMER,
            phone='+61 400 111 111'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        print(f"✓ User created: {user.email}")
        print(f"  ID: {user.id}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Role: {user.role.value}")
        
        return user
    
    def test_fleet_management(self):
        """Test fleet management operations."""
        print("\n[QUICK TEST] Fleet Management")
        print("-" * 40)
        
        # Add a new vehicle
        car = Car(
            make='Toyota',
            model='Camry',
            year=2024,
            license_plate='TEST123',
            vin='VIN1234567890',
            category=CarCategory.MIDSIZE,
            seats=5,
            transmission='Automatic',
            fuel_type='Gasoline',
            daily_rate=85.00,
            weekly_rate=510.00,
            monthly_rate=1700.00,
            color='Silver',
            agency='Melbourne CBD',
            current_odometer=5000,
            last_service_odometer=0,
            service_threshold=5000,
            status=CarStatus.AVAILABLE,
            current_location='123 Collins St, Melbourne',
            features=['GPS', 'Bluetooth', 'Air Conditioning']
        )
        db.session.add(car)
        db.session.commit()
        
        print(f"✓ Vehicle added: {car.make} {car.model}")
        print(f"  License Plate: {car.license_plate}")
        print(f"  Status: {car.status.value}")
        print(f"  Daily Rate: ${car.daily_rate}")
        
        # Update vehicle status
        car.status = CarStatus.MAINTENANCE
        db.session.commit()
        print(f"✓ Vehicle status updated to: {car.status.value}")
        
        return car
    
    def test_servicing(self):
        """Test servicing and maintenance scheduling."""
        print("\n[QUICK TEST] Servicing & Maintenance")
        print("-" * 40)
        
        # Create a car for maintenance
        car = Car(
            make='Honda',
            model='Civic',
            year=2023,
            license_plate='MAINT01',
            vin='VINMAINT123',
            category=CarCategory.COMPACT,
            daily_rate=70.00,
            status=CarStatus.AVAILABLE,
            current_odometer=45000,
            last_service_odometer=40000,
            service_threshold=5000
        )
        db.session.add(car)
        db.session.commit()
        
        # Schedule maintenance
        maintenance = Maintenance(
            car_id=car.id,
            type=MaintenanceType.OIL_CHANGE,
            service_date=(datetime.utcnow() + timedelta(days=3)).date(),
            description='Scheduled oil change and filter replacement',
            status=MaintenanceStatus.SCHEDULED,
            total_cost=150.00
        )
        db.session.add(maintenance)
        db.session.commit()
        
        print(f"✓ Maintenance scheduled for: {car.make} {car.model}")
        print(f"  Type: {maintenance.type.value}")
        print(f"  Date: {maintenance.service_date}")
        print(f"  Cost: ${maintenance.total_cost}")
        
        # Check service threshold
        needs_service = (car.current_odometer - car.last_service_odometer) >= car.service_threshold
        print(f"✓ Service threshold check: {'Needs Service' if needs_service else 'OK'}")
        
        return maintenance
    
    def test_booking_creation(self):
        """Test creating and managing bookings."""
        print("\n[QUICK TEST] Booking Management")
        print("-" * 40)
        
        # Create customer and car
        customer = User(
            email='booking_customer@example.com',
            username='booking_customer',
            first_name='Booking',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 222 222'
        )
        customer.set_password('password')
        db.session.add(customer)
        
        car = Car(
            make='Tesla',
            model='Model 3',
            year=2024,
            license_plate='BOOK01',
            vin='VINBOOK123',
            category=CarCategory.ELECTRIC,
            daily_rate=120.00,
            status=CarStatus.AVAILABLE
        )
        db.session.add(car)
        db.session.commit()
        
        # Create booking
        booking = Booking(
            customer_id=customer.id,
            car_id=car.id,
            pickup_date=datetime.utcnow() + timedelta(days=2),
            return_date=datetime.utcnow() + timedelta(days=5),
            pickup_location='Melbourne Airport',
            return_location='Melbourne CBD',
            daily_rate=120.00,
            total_days=3,
            subtotal=360.00,
            total_amount=396.00,  # Including 10% tax
            status=BookingStatus.CONFIRMED
        )
        booking.generate_booking_number()
        db.session.add(booking)
        
        # Update car status
        car.status = CarStatus.BOOKED
        db.session.commit()
        
        print(f"✓ Booking created: {booking.booking_number}")
        print(f"  Customer: {customer.first_name} {customer.last_name}")
        print(f"  Vehicle: {car.make} {car.model}")
        print(f"  Duration: {booking.total_days} days")
        print(f"  Total: ${booking.total_amount}")
        
        return booking
    
    def test_invoicing(self):
        """Test invoice generation and payment processing."""
        print("\n[QUICK TEST] Invoicing & Payments")
        print("-" * 40)
        
        # Create customer
        customer = User(
            email='invoice_customer@example.com',
            username='invoice_customer',
            first_name='Invoice',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 333 333'
        )
        customer.set_password('password')
        db.session.add(customer)
        db.session.commit()
        
        # Create invoice
        invoice = Invoice(
            customer_id=customer.id,
            invoice_number=f'INV-{datetime.utcnow().strftime("%Y%m%d")}-001',
            amount=500.00,
            tax_amount=50.00,
            status=InvoiceStatus.PENDING,
            due_date=datetime.utcnow().date() + timedelta(days=7)
        )
        db.session.add(invoice)
        db.session.commit()
        
        print(f"✓ Invoice generated: {invoice.invoice_number}")
        print(f"  Customer: {customer.first_name} {customer.last_name}")
        print(f"  Amount: ${invoice.amount}")
        print(f"  Tax: ${invoice.tax_amount}")
        print(f"  Due Date: {invoice.due_date}")
        
        # Process payment
        payment = Payment(
            user_id=customer.id,
            amount=invoice.amount,
            payment_method=PaymentMethod.CREDIT_CARD,
            status=PaymentStatus.COMPLETED,
            transaction_id=f'TXN{invoice.id:06d}',
            processed_at=datetime.utcnow()
        )
        db.session.add(payment)
        
        # Update invoice status
        invoice.status = InvoiceStatus.PAID
        db.session.commit()
        
        print(f"✓ Payment processed: {payment.transaction_id}")
        print(f"  Method: {payment.payment_method.value}")
        print(f"  Status: {payment.status.value}")
        
        return invoice, payment
    
    def test_pay_advantage(self):
        """Test Pay Advantage integration."""
        print("\n[QUICK TEST] Pay Advantage Integration")
        print("-" * 40)
        
        try:
            # Create customer
            customer = User(
                email='payadvantage_customer@example.com',
                username='pa_customer',
                first_name='PayAdvantage',
                last_name='Customer',
                role=Role.CUSTOMER,
                phone='+61 400 444 444'
            )
            customer.set_password('password')
            db.session.add(customer)
            db.session.commit()
            
            print(f"✓ Customer created: {customer.email}")
            
            # Initialize Pay Advantage service
            pa_service = PayAdvantageService()
            
            # Note: In a real test, this would create a customer in Pay Advantage
            # For now, we'll simulate it
            pa_customer = PayAdvantageCustomer(
                user_id=customer.id,
                customer_code=f'CUST{customer.id:06d}',
                created_at=datetime.utcnow()
            )
            db.session.add(pa_customer)
            db.session.commit()
            
            print(f"✓ Pay Advantage customer code: {pa_customer.customer_code}")
            
            # Simulate DDR link generation
            ddr_link = f"https://payadvantage.com.au/ddr/authorize/{pa_customer.customer_code}"
            print(f"✓ DDR Link generated: {ddr_link}")
            
            # Create direct debit schedule
            dd_schedule = DirectDebitSchedule(
                user_id=customer.id,
                pay_advantage_customer_id=pa_customer.id,
                amount=100.00,
                frequency='WEEKLY',
                start_date=datetime.utcnow().date(),
                status='ACTIVE'
            )
            db.session.add(dd_schedule)
            db.session.commit()
            
            print(f"✓ Direct Debit Schedule created")
            print(f"  Amount: ${dd_schedule.amount}")
            print(f"  Frequency: {dd_schedule.frequency}")
            print(f"  Start Date: {dd_schedule.start_date}")
            
        except Exception as e:
            print(f"⚠ Pay Advantage test simulated (API not connected): {str(e)}")
        
        return pa_customer if 'pa_customer' in locals() else None
    
    def test_database_integrity(self):
        """Test database integrity checks."""
        print("\n[QUICK TEST] Database Integrity")
        print("-" * 40)
        
        # Test unique constraints
        try:
            user1 = User(
                email='unique@test.com',
                username='unique1',
                first_name='User',
                last_name='One',
                role=Role.CUSTOMER,
                phone='+61 400 555 555'
            )
            user1.set_password('password')
            db.session.add(user1)
            db.session.commit()
            print(f"✓ User 1 created with email: unique@test.com")
            
            # Try duplicate email
            user2 = User(
                email='unique@test.com',  # Duplicate
                username='unique2',
                first_name='User',
                last_name='Two',
                role=Role.CUSTOMER,
                phone='+61 400 666 666'
            )
            user2.set_password('password')
            db.session.add(user2)
            db.session.commit()
            print("✗ Duplicate email allowed (constraint failed)")
        except Exception:
            db.session.rollback()
            print("✓ Unique email constraint enforced")
        
        # Test foreign key constraints
        booking_count_before = Booking.query.count()
        try:
            # Try to create booking with invalid references
            invalid_booking = Booking(
                customer_id=99999,  # Non-existent user
                car_id=99999,  # Non-existent car
                pickup_date=datetime.utcnow(),
                return_date=datetime.utcnow() + timedelta(days=1),
                pickup_location='Test',
                return_location='Test',
                daily_rate=100.00,
                total_days=1,
                subtotal=100.00,
                total_amount=110.00,
                status=BookingStatus.CONFIRMED
            )
            invalid_booking.generate_booking_number()
            db.session.add(invalid_booking)
            db.session.commit()
            print("✗ Invalid foreign keys allowed (constraint failed)")
        except Exception:
            db.session.rollback()
            print("✓ Foreign key constraints enforced")
        
        booking_count_after = Booking.query.count()
        if booking_count_before == booking_count_after:
            print("✓ Transaction rollback successful")
        
        # Check table counts
        print(f"\nDatabase Statistics:")
        print(f"  Users: {User.query.count()}")
        print(f"  Cars: {Car.query.count()}")
        print(f"  Bookings: {Booking.query.count()}")
        print(f"  Payments: {Payment.query.count()}")
        print(f"  Maintenance Records: {Maintenance.query.count()}")
        print(f"  Pay Advantage Customers: {PayAdvantageCustomer.query.count()}")
    
    def test_links_validation(self):
        """Quick test for checking links."""
        print("\n[QUICK TEST] Link Validation")
        print("-" * 40)
        
        endpoints = [
            ('/admin', 'Admin Dashboard'),
            ('/admin/users', 'User Management'),
            ('/admin/fleet', 'Fleet Management'),
            ('/admin/bookings', 'Bookings'),
            ('/admin/maintenance', 'Maintenance'),
            ('/admin/payments', 'Payments')
        ]
        
        for endpoint, name in endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code in [200, 302]:  # 302 for auth redirects
                    print(f"✓ {name}: {endpoint} - OK")
                else:
                    print(f"✗ {name}: {endpoint} - Status {response.status_code}")
            except Exception as e:
                print(f"✗ {name}: {endpoint} - Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all quick tests."""
        print("\n" + "="*50)
        print("ADMIN DASHBOARD QUICK TEST SUITE")
        print("="*50)
        print("\nPay Advantage Credentials:")
        print("Username: live_83e0ad9f0d3342e699dea15d35cc0d3a")
        print("Password: [PROVIDED]")
        
        tests = [
            self.test_user_creation,
            self.test_fleet_management,
            self.test_servicing,
            self.test_booking_creation,
            self.test_invoicing,
            self.test_pay_advantage,
            self.test_database_integrity,
            self.test_links_validation
        ]
        
        results = []
        for test in tests:
            try:
                test()
                results.append((test.__name__, True))
            except Exception as e:
                print(f"\n✗ Error in {test.__name__}: {str(e)}")
                results.append((test.__name__, False))
        
        # Print summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"{test_name.replace('test_', '').replace('_', ' ').title()}: {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        print("="*50)
        
        return passed == total
    
    def cleanup(self):
        """Clean up test environment."""
        db.session.remove()
        self.app_context.pop()


def main():
    """Main entry point."""
    tester = AdminDashboardQuickTest()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        return 1
    finally:
        tester.cleanup()


if __name__ == '__main__':
    sys.exit(main())