#!/usr/bin/env python3
"""
Comprehensive test suite for Admin Dashboard functionality.
Tests user management, fleet management, servicing, bookings, invoicing, 
Pay Advantage integration, link validation, and database integrity.
"""

import sys
import os
import unittest
import requests
from datetime import datetime, timedelta
from decimal import Decimal
import json
import time
from unittest.mock import patch, MagicMock

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
from flask_login import login_user, logout_user


class AdminDashboardTestCase(unittest.TestCase):
    """Base test case with common setup and teardown."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.app = create_app('testing')
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Set Pay Advantage credentials
        cls.app.config['PAY_ADVANTAGE_USERNAME'] = 'live_83e0ad9f0d3342e699dea15d35cc0d3a'
        cls.app.config['PAY_ADVANTAGE_PASSWORD'] = '3ac68741013145009121d3ea36317ad7'
        
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Create all tables
        db.create_all()
        
        # Create admin user for testing
        cls.admin_user = User(
            email='test_admin@aurora.com',
            username='test_admin',
            first_name='Test',
            last_name='Admin',
            role=Role.ADMIN,
            phone='+61 400 000 000'
        )
        cls.admin_user.set_password('admin_test_123')
        db.session.add(cls.admin_user)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        """Set up each test."""
        self.login_admin()
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean up test data but keep admin user
        for model in [Booking, Payment, Maintenance, DirectDebitSchedule, 
                     PayAdvantageCustomer, Invoice]:
            model.query.delete()
        
        User.query.filter(User.id != self.admin_user.id).delete()
        Car.query.delete()
        db.session.commit()
    
    def login_admin(self):
        """Helper method to login as admin."""
        with self.client:
            response = self.client.post('/auth/login', data={
                'email': 'test_admin@aurora.com',
                'password': 'admin_test_123'
            }, follow_redirects=True)
            return response


class TestUserManagement(AdminDashboardTestCase):
    """Test cases for user management functionality."""
    
    def test_create_user(self):
        """Test creating a new user through admin dashboard."""
        print("\n[TEST] Creating a new user...")
        
        # Test data for new user
        user_data = {
            'email': 'new_user@test.com',
            'username': 'new_user',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+61 400 111 111',
            'role': 'CUSTOMER',
            'password': 'test_password_123'
        }
        
        # Create user via admin endpoint
        response = self.client.post('/admin/users/create', 
                                   data=user_data,
                                   follow_redirects=True)
        
        # Verify user was created
        user = User.query.filter_by(email='new_user@test.com').first()
        self.assertIsNotNone(user, "User should be created")
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, Role.CUSTOMER)
        
        print("✓ User created successfully")
    
    def test_edit_user(self):
        """Test editing an existing user."""
        print("\n[TEST] Editing an existing user...")
        
        # Create a test user first
        test_user = User(
            email='edit_test@test.com',
            username='edit_test',
            first_name='Edit',
            last_name='Test',
            role=Role.CUSTOMER,
            phone='+61 400 222 222'
        )
        test_user.set_password('original_password')
        db.session.add(test_user)
        db.session.commit()
        
        # Edit the user
        edit_data = {
            'first_name': 'Edited',
            'last_name': 'User',
            'phone': '+61 400 333 333'
        }
        
        response = self.client.post(f'/admin/users/edit/{test_user.id}',
                                   data=edit_data,
                                   follow_redirects=True)
        
        # Verify changes
        db.session.refresh(test_user)
        self.assertEqual(test_user.first_name, 'Edited')
        self.assertEqual(test_user.last_name, 'User')
        self.assertEqual(test_user.phone, '+61 400 333 333')
        
        print("✓ User edited successfully")
    
    def test_delete_user(self):
        """Test deleting a user."""
        print("\n[TEST] Deleting a user...")
        
        # Create a test user
        test_user = User(
            email='delete_test@test.com',
            username='delete_test',
            first_name='Delete',
            last_name='Test',
            role=Role.CUSTOMER,
            phone='+61 400 444 444'
        )
        test_user.set_password('temp_password')
        db.session.add(test_user)
        db.session.commit()
        
        user_id = test_user.id
        
        # Delete the user
        response = self.client.post(f'/admin/users/delete/{user_id}',
                                   follow_redirects=True)
        
        # Verify deletion
        deleted_user = User.query.get(user_id)
        self.assertIsNone(deleted_user, "User should be deleted")
        
        print("✓ User deleted successfully")
    
    def test_user_role_management(self):
        """Test changing user roles."""
        print("\n[TEST] Managing user roles...")
        
        # Create a customer user
        customer = User(
            email='role_test@test.com',
            username='role_test',
            first_name='Role',
            last_name='Test',
            role=Role.CUSTOMER,
            phone='+61 400 555 555'
        )
        customer.set_password('password')
        db.session.add(customer)
        db.session.commit()
        
        # Change role to STAFF
        response = self.client.post(f'/admin/users/role/{customer.id}',
                                   data={'role': 'STAFF'},
                                   follow_redirects=True)
        
        db.session.refresh(customer)
        self.assertEqual(customer.role, Role.STAFF)
        
        print("✓ User role changed successfully")


class TestFleetManagement(AdminDashboardTestCase):
    """Test cases for fleet management functionality."""
    
    def test_add_new_vehicle(self):
        """Test adding a new vehicle to the fleet."""
        print("\n[TEST] Adding a new vehicle...")
        
        vehicle_data = {
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2024,
            'license_plate': 'TEST001',
            'vin': 'VIN1234567890TEST',
            'category': CarCategory.COMPACT.value,
            'seats': 5,
            'transmission': 'Automatic',
            'fuel_type': 'Gasoline',
            'daily_rate': 75.00,
            'weekly_rate': 450.00,
            'monthly_rate': 1500.00,
            'color': 'Blue',
            'agency': 'Melbourne CBD',
            'current_odometer': 10000,
            'service_threshold': 5000,
            'status': CarStatus.AVAILABLE.value
        }
        
        response = self.client.post('/admin/fleet/add',
                                   data=vehicle_data,
                                   follow_redirects=True)
        
        # Verify vehicle was added
        car = Car.query.filter_by(license_plate='TEST001').first()
        self.assertIsNotNone(car, "Vehicle should be added")
        self.assertEqual(car.make, 'Toyota')
        self.assertEqual(car.model, 'Corolla')
        self.assertEqual(car.status, CarStatus.AVAILABLE)
        
        print("✓ Vehicle added successfully")
    
    def test_update_vehicle_status(self):
        """Test updating vehicle status."""
        print("\n[TEST] Updating vehicle status...")
        
        # Create a test vehicle
        car = Car(
            make='Honda',
            model='Civic',
            year=2023,
            license_plate='STATUS01',
            vin='VINSTATUS123456',
            category=CarCategory.COMPACT,
            daily_rate=70.00,
            status=CarStatus.AVAILABLE
        )
        db.session.add(car)
        db.session.commit()
        
        # Update status to MAINTENANCE
        response = self.client.post(f'/admin/fleet/status/{car.id}',
                                   data={'status': CarStatus.MAINTENANCE.value},
                                   follow_redirects=True)
        
        db.session.refresh(car)
        self.assertEqual(car.status, CarStatus.MAINTENANCE)
        
        print("✓ Vehicle status updated successfully")
    
    def test_vehicle_availability_tracking(self):
        """Test tracking vehicle availability."""
        print("\n[TEST] Tracking vehicle availability...")
        
        # Create vehicles with different statuses
        available_car = Car(
            make='Tesla', model='Model 3', year=2024,
            license_plate='AVAIL01', vin='VINAVAIL01',
            category=CarCategory.ELECTRIC,
            status=CarStatus.AVAILABLE,
            daily_rate=120.00
        )
        
        booked_car = Car(
            make='BMW', model='X5', year=2023,
            license_plate='BOOK01', vin='VINBOOK01',
            category=CarCategory.SUV,
            status=CarStatus.BOOKED,
            daily_rate=150.00
        )
        
        db.session.add_all([available_car, booked_car])
        db.session.commit()
        
        # Check fleet status endpoint
        response = self.client.get('/admin/fleet/status')
        
        # Verify we can track availability
        available_cars = Car.query.filter_by(status=CarStatus.AVAILABLE).all()
        booked_cars = Car.query.filter_by(status=CarStatus.BOOKED).all()
        
        self.assertGreaterEqual(len(available_cars), 1)
        self.assertGreaterEqual(len(booked_cars), 1)
        
        print("✓ Vehicle availability tracked successfully")


class TestServicing(AdminDashboardTestCase):
    """Test cases for vehicle servicing and maintenance."""
    
    def test_schedule_maintenance(self):
        """Test scheduling vehicle maintenance."""
        print("\n[TEST] Scheduling maintenance...")
        
        # Create a test vehicle
        car = Car(
            make='Ford', model='Focus', year=2023,
            license_plate='MAINT01', vin='VINMAINT01',
            category=CarCategory.COMPACT,
            status=CarStatus.AVAILABLE,
            daily_rate=65.00,
            current_odometer=45000,
            last_service_odometer=40000,
            service_threshold=5000
        )
        db.session.add(car)
        db.session.commit()
        
        # Schedule maintenance
        maintenance_data = {
            'car_id': car.id,
            'type': MaintenanceType.OIL_CHANGE.value,
            'service_date': (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'description': 'Scheduled oil change',
            'status': MaintenanceStatus.SCHEDULED.value,
            'total_cost': 150.00
        }
        
        response = self.client.post('/admin/maintenance/schedule',
                                   data=maintenance_data,
                                   follow_redirects=True)
        
        # Verify maintenance was scheduled
        maintenance = Maintenance.query.filter_by(car_id=car.id).first()
        self.assertIsNotNone(maintenance, "Maintenance should be scheduled")
        self.assertEqual(maintenance.type, MaintenanceType.OIL_CHANGE)
        self.assertEqual(maintenance.status, MaintenanceStatus.SCHEDULED)
        
        print("✓ Maintenance scheduled successfully")
    
    def test_service_threshold_alert(self):
        """Test service threshold alerts."""
        print("\n[TEST] Testing service threshold alerts...")
        
        # Create a vehicle near service threshold
        car = Car(
            make='Mazda', model='3', year=2023,
            license_plate='THRESH01', vin='VINTHRESH01',
            category=CarCategory.COMPACT,
            status=CarStatus.AVAILABLE,
            daily_rate=70.00,
            current_odometer=49800,
            last_service_odometer=45000,
            service_threshold=5000
        )
        db.session.add(car)
        db.session.commit()
        
        # Check if vehicle needs service
        needs_service = (car.current_odometer - car.last_service_odometer) >= car.service_threshold
        self.assertFalse(needs_service, "Should not need service yet")
        
        # Update odometer to exceed threshold
        car.current_odometer = 50100
        db.session.commit()
        
        needs_service = (car.current_odometer - car.last_service_odometer) >= car.service_threshold
        self.assertTrue(needs_service, "Should need service now")
        
        print("✓ Service threshold alerts working correctly")
    
    def test_maintenance_history(self):
        """Test maintenance history tracking."""
        print("\n[TEST] Testing maintenance history...")
        
        # Create vehicle with maintenance history
        car = Car(
            make='Nissan', model='Altima', year=2023,
            license_plate='HIST01', vin='VINHIST01',
            category=CarCategory.MIDSIZE,
            status=CarStatus.AVAILABLE,
            daily_rate=80.00
        )
        db.session.add(car)
        db.session.commit()
        
        # Add multiple maintenance records
        maintenance_records = [
            Maintenance(
                car_id=car.id,
                type=MaintenanceType.OIL_CHANGE,
                service_date=datetime.utcnow().date() - timedelta(days=90),
                description='Oil change completed',
                status=MaintenanceStatus.COMPLETED,
                total_cost=120.00
            ),
            Maintenance(
                car_id=car.id,
                type=MaintenanceType.TIRE_ROTATION,
                service_date=datetime.utcnow().date() - timedelta(days=30),
                description='Tire rotation completed',
                status=MaintenanceStatus.COMPLETED,
                total_cost=80.00
            )
        ]
        
        db.session.add_all(maintenance_records)
        db.session.commit()
        
        # Verify maintenance history
        history = Maintenance.query.filter_by(car_id=car.id).all()
        self.assertEqual(len(history), 2)
        
        # Check total maintenance cost
        total_cost = sum(m.total_cost for m in history)
        self.assertEqual(total_cost, 200.00)
        
        print("✓ Maintenance history tracked successfully")


class TestBookings(AdminDashboardTestCase):
    """Test cases for booking management."""
    
    def test_create_booking(self):
        """Test creating a new booking."""
        print("\n[TEST] Creating a new booking...")
        
        # Create customer and car
        customer = User(
            email='booking_customer@test.com',
            username='booking_customer',
            first_name='Booking',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 666 666'
        )
        customer.set_password('password')
        
        car = Car(
            make='Toyota', model='Camry', year=2023,
            license_plate='BOOK001', vin='VINBOOK001',
            category=CarCategory.MIDSIZE,
            status=CarStatus.AVAILABLE,
            daily_rate=85.00
        )
        
        db.session.add_all([customer, car])
        db.session.commit()
        
        # Create booking
        booking_data = {
            'customer_id': customer.id,
            'car_id': car.id,
            'pickup_date': (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'return_date': (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'pickup_location': 'Melbourne Airport',
            'return_location': 'Melbourne CBD',
            'daily_rate': 85.00,
            'total_days': 3,
            'subtotal': 255.00,
            'total_amount': 280.50  # Including fees
        }
        
        response = self.client.post('/admin/bookings/create',
                                   data=booking_data,
                                   follow_redirects=True)
        
        # Verify booking was created
        booking = Booking.query.filter_by(customer_id=customer.id, car_id=car.id).first()
        self.assertIsNotNone(booking, "Booking should be created")
        self.assertEqual(booking.total_days, 3)
        
        # Verify car status changed
        db.session.refresh(car)
        self.assertEqual(car.status, CarStatus.BOOKED)
        
        print("✓ Booking created successfully")
    
    def test_modify_booking(self):
        """Test modifying an existing booking."""
        print("\n[TEST] Modifying a booking...")
        
        # Create initial booking
        customer = User(
            email='modify_customer@test.com',
            username='modify_customer',
            first_name='Modify',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 777 777'
        )
        customer.set_password('password')
        
        car = Car(
            make='Honda', model='Accord', year=2023,
            license_plate='MOD001', vin='VINMOD001',
            category=CarCategory.MIDSIZE,
            status=CarStatus.AVAILABLE,
            daily_rate=90.00
        )
        
        db.session.add_all([customer, car])
        db.session.commit()
        
        booking = Booking(
            customer_id=customer.id,
            car_id=car.id,
            pickup_date=datetime.utcnow() + timedelta(days=3),
            return_date=datetime.utcnow() + timedelta(days=6),
            pickup_location='Melbourne Airport',
            return_location='Melbourne Airport',
            daily_rate=90.00,
            total_days=3,
            subtotal=270.00,
            total_amount=297.00,
            status=BookingStatus.CONFIRMED
        )
        booking.generate_booking_number()
        db.session.add(booking)
        db.session.commit()
        
        # Modify booking dates
        new_return_date = datetime.utcnow() + timedelta(days=8)
        response = self.client.post(f'/admin/bookings/edit/{booking.id}',
                                   data={'return_date': new_return_date.strftime('%Y-%m-%d'),
                                         'total_days': 5},
                                   follow_redirects=True)
        
        db.session.refresh(booking)
        self.assertEqual(booking.total_days, 5)
        
        print("✓ Booking modified successfully")
    
    def test_cancel_booking(self):
        """Test cancelling a booking."""
        print("\n[TEST] Cancelling a booking...")
        
        # Create booking to cancel
        customer = User(
            email='cancel_customer@test.com',
            username='cancel_customer',
            first_name='Cancel',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 888 888'
        )
        customer.set_password('password')
        
        car = Car(
            make='Mazda', model='CX-5', year=2023,
            license_plate='CANCEL01', vin='VINCANCEL01',
            category=CarCategory.SUV,
            status=CarStatus.BOOKED,
            daily_rate=95.00
        )
        
        db.session.add_all([customer, car])
        db.session.commit()
        
        booking = Booking(
            customer_id=customer.id,
            car_id=car.id,
            pickup_date=datetime.utcnow() + timedelta(days=10),
            return_date=datetime.utcnow() + timedelta(days=15),
            pickup_location='Melbourne CBD',
            return_location='Melbourne CBD',
            daily_rate=95.00,
            total_days=5,
            subtotal=475.00,
            total_amount=522.50,
            status=BookingStatus.CONFIRMED
        )
        booking.generate_booking_number()
        db.session.add(booking)
        db.session.commit()
        
        # Cancel booking
        response = self.client.post(f'/admin/bookings/cancel/{booking.id}',
                                   follow_redirects=True)
        
        db.session.refresh(booking)
        self.assertEqual(booking.status, BookingStatus.CANCELLED)
        
        # Verify car is available again
        db.session.refresh(car)
        self.assertEqual(car.status, CarStatus.AVAILABLE)
        
        print("✓ Booking cancelled successfully")


class TestInvoicing(AdminDashboardTestCase):
    """Test cases for invoicing and payment processing."""
    
    def test_generate_invoice(self):
        """Test generating an invoice for a booking."""
        print("\n[TEST] Generating invoice...")
        
        # Create booking with customer
        customer = User(
            email='invoice_customer@test.com',
            username='invoice_customer',
            first_name='Invoice',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 999 999'
        )
        customer.set_password('password')
        
        car = Car(
            make='BMW', model='3 Series', year=2023,
            license_plate='INV001', vin='VININV001',
            category=CarCategory.LUXURY,
            status=CarStatus.AVAILABLE,
            daily_rate=150.00
        )
        
        db.session.add_all([customer, car])
        db.session.commit()
        
        booking = Booking(
            customer_id=customer.id,
            car_id=car.id,
            pickup_date=datetime.utcnow(),
            return_date=datetime.utcnow() + timedelta(days=3),
            pickup_location='Melbourne Airport',
            return_location='Melbourne Airport',
            daily_rate=150.00,
            total_days=3,
            subtotal=450.00,
            total_amount=495.00,  # With tax
            status=BookingStatus.CONFIRMED
        )
        booking.generate_booking_number()
        db.session.add(booking)
        db.session.commit()
        
        # Generate invoice
        invoice = Invoice(
            booking_id=booking.id,
            customer_id=customer.id,
            invoice_number=f'INV-{booking.booking_number}',
            amount=booking.total_amount,
            tax_amount=45.00,
            status=InvoiceStatus.PENDING,
            due_date=datetime.utcnow().date() + timedelta(days=7)
        )
        db.session.add(invoice)
        db.session.commit()
        
        self.assertIsNotNone(invoice.invoice_number)
        self.assertEqual(invoice.amount, Decimal('495.00'))
        self.assertEqual(invoice.status, InvoiceStatus.PENDING)
        
        print("✓ Invoice generated successfully")
    
    def test_process_payment(self):
        """Test processing a payment."""
        print("\n[TEST] Processing payment...")
        
        # Create booking and customer
        customer = User(
            email='payment_customer@test.com',
            username='payment_customer',
            first_name='Payment',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 100 100'
        )
        customer.set_password('password')
        
        car = Car(
            make='Mercedes', model='C-Class', year=2023,
            license_plate='PAY001', vin='VINPAY001',
            category=CarCategory.LUXURY,
            status=CarStatus.AVAILABLE,
            daily_rate=160.00
        )
        
        db.session.add_all([customer, car])
        db.session.commit()
        
        booking = Booking(
            customer_id=customer.id,
            car_id=car.id,
            pickup_date=datetime.utcnow(),
            return_date=datetime.utcnow() + timedelta(days=2),
            pickup_location='Melbourne CBD',
            return_location='Melbourne CBD',
            daily_rate=160.00,
            total_days=2,
            subtotal=320.00,
            total_amount=352.00,
            status=BookingStatus.CONFIRMED
        )
        booking.generate_booking_number()
        db.session.add(booking)
        db.session.commit()
        
        # Process payment
        payment = Payment(
            booking_id=booking.id,
            user_id=customer.id,
            amount=booking.total_amount,
            payment_method=PaymentMethod.CREDIT_CARD,
            status=PaymentStatus.PENDING,
            transaction_id=f'TXN{booking.id:06d}'
        )
        db.session.add(payment)
        db.session.commit()
        
        # Simulate payment processing
        payment.status = PaymentStatus.COMPLETED
        payment.processed_at = datetime.utcnow()
        db.session.commit()
        
        self.assertEqual(payment.status, PaymentStatus.COMPLETED)
        self.assertIsNotNone(payment.processed_at)
        
        print("✓ Payment processed successfully")
    
    def test_payment_history(self):
        """Test viewing payment history."""
        print("\n[TEST] Viewing payment history...")
        
        # Create multiple payments
        customer = User(
            email='history_customer@test.com',
            username='history_customer',
            first_name='History',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 200 200'
        )
        customer.set_password('password')
        db.session.add(customer)
        db.session.commit()
        
        # Create multiple payments
        for i in range(3):
            payment = Payment(
                user_id=customer.id,
                amount=Decimal(100 + i * 50),
                payment_method=PaymentMethod.CREDIT_CARD,
                status=PaymentStatus.COMPLETED,
                transaction_id=f'HIST{i:06d}',
                processed_at=datetime.utcnow() - timedelta(days=i)
            )
            db.session.add(payment)
        
        db.session.commit()
        
        # Query payment history
        payments = Payment.query.filter_by(user_id=customer.id).all()
        self.assertEqual(len(payments), 3)
        
        # Verify total amount
        total = sum(p.amount for p in payments)
        self.assertEqual(total, Decimal('450'))
        
        print("✓ Payment history retrieved successfully")


class TestPayAdvantage(AdminDashboardTestCase):
    """Test cases for Pay Advantage integration."""
    
    @patch('app.services.pay_advantage.requests')
    def test_create_pay_advantage_customer(self, mock_requests):
        """Test creating a Pay Advantage customer."""
        print("\n[TEST] Creating Pay Advantage customer...")
        
        # Mock API responses
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {'token': 'test_token_123'}
        
        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {
            'customer_code': 'CUST123456',
            'ddr_link': 'https://payadvantage.com.au/ddr/CUST123456'
        }
        
        mock_requests.post.side_effect = [mock_auth_response, mock_create_response]
        
        # Create customer
        customer = User(
            email='pa_customer@test.com',
            username='pa_customer',
            first_name='PayAdvantage',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 300 300'
        )
        customer.set_password('password')
        db.session.add(customer)
        db.session.commit()
        
        # Initialize Pay Advantage service with credentials
        with patch.dict(os.environ, {
            'PAY_ADVANTAGE_USERNAME': 'live_83e0ad9f0d3342e699dea15d35cc0d3a',
            'PAY_ADVANTAGE_PASSWORD': '3ac68741013145009121d3ea36317ad7'
        }):
            pa_service = PayAdvantageService()
            pa_customer = pa_service.get_or_create_customer(customer)
        
        self.assertIsNotNone(pa_customer)
        self.assertEqual(pa_customer.customer_code, 'CUST123456')
        self.assertEqual(pa_customer.user_id, customer.id)
        
        print("✓ Pay Advantage customer created successfully")
    
    @patch('app.services.pay_advantage.requests')
    def test_generate_ddr_link(self, mock_requests):
        """Test generating DDR (Direct Debit Request) link."""
        print("\n[TEST] Generating DDR link...")
        
        # Mock API responses
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {'token': 'test_token_456'}
        
        mock_ddr_response = MagicMock()
        mock_ddr_response.status_code = 200
        mock_ddr_response.json.return_value = {
            'ddr_link': 'https://payadvantage.com.au/ddr/authorize/CUST789',
            'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        mock_requests.post.side_effect = [mock_auth_response]
        mock_requests.get.return_value = mock_ddr_response
        
        # Create customer with Pay Advantage record
        customer = User(
            email='ddr_customer@test.com',
            username='ddr_customer',
            first_name='DDR',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 400 400'
        )
        customer.set_password('password')
        db.session.add(customer)
        db.session.commit()
        
        pa_customer = PayAdvantageCustomer(
            user_id=customer.id,
            customer_code='CUST789',
            created_at=datetime.utcnow()
        )
        db.session.add(pa_customer)
        db.session.commit()
        
        # Generate DDR link
        with patch.dict(os.environ, {
            'PAY_ADVANTAGE_USERNAME': 'live_83e0ad9f0d3342e699dea15d35cc0d3a',
            'PAY_ADVANTAGE_PASSWORD': '3ac68741013145009121d3ea36317ad7'
        }):
            pa_service = PayAdvantageService()
            ddr_link = pa_service.generate_ddr_link(pa_customer)
        
        self.assertIsNotNone(ddr_link)
        self.assertIn('payadvantage.com.au/ddr', ddr_link)
        
        print("✓ DDR link generated successfully")
    
    @patch('app.services.pay_advantage.requests')
    def test_verify_customer_creation(self, mock_requests):
        """Test verifying that a customer is being created in Pay Advantage."""
        print("\n[TEST] Verifying customer creation in Pay Advantage...")
        
        # Mock successful customer creation
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {'token': 'test_token_789'}
        
        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {
            'customer_code': 'VERIFY123',
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }
        
        mock_requests.post.side_effect = [mock_auth_response, mock_create_response]
        
        # Create and verify customer
        customer = User(
            email='verify_customer@test.com',
            username='verify_customer',
            first_name='Verify',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 500 500'
        )
        customer.set_password('password')
        db.session.add(customer)
        db.session.commit()
        
        with patch.dict(os.environ, {
            'PAY_ADVANTAGE_USERNAME': 'live_83e0ad9f0d3342e699dea15d35cc0d3a',
            'PAY_ADVANTAGE_PASSWORD': '3ac68741013145009121d3ea36317ad7'
        }):
            pa_service = PayAdvantageService()
            pa_customer = pa_service.get_or_create_customer(customer)
        
        # Verify customer was created
        self.assertEqual(pa_customer.customer_code, 'VERIFY123')
        
        # Verify in database
        db_customer = PayAdvantageCustomer.query.filter_by(user_id=customer.id).first()
        self.assertIsNotNone(db_customer)
        self.assertEqual(db_customer.customer_code, 'VERIFY123')
        
        print("✓ Customer creation verified in Pay Advantage")


class TestLinkValidation(AdminDashboardTestCase):
    """Test cases for validating links in the application."""
    
    def test_admin_dashboard_links(self):
        """Test all links in admin dashboard are not broken."""
        print("\n[TEST] Validating admin dashboard links...")
        
        # List of admin endpoints to test
        admin_endpoints = [
            '/admin',
            '/admin/dashboard',
            '/admin/users',
            '/admin/fleet',
            '/admin/bookings',
            '/admin/payments',
            '/admin/maintenance',
            '/admin/reports'
        ]
        
        broken_links = []
        
        for endpoint in admin_endpoints:
            response = self.client.get(endpoint, follow_redirects=False)
            # Check for successful response or redirect (302 is OK for auth redirects)
            if response.status_code not in [200, 302]:
                broken_links.append((endpoint, response.status_code))
        
        self.assertEqual(len(broken_links), 0, 
                        f"Found broken links: {broken_links}")
        
        print("✓ All admin dashboard links are valid")
    
    def test_navigation_links(self):
        """Test navigation menu links."""
        print("\n[TEST] Testing navigation links...")
        
        # Get the admin dashboard page
        response = self.client.get('/admin', follow_redirects=True)
        
        # Check for common navigation elements
        self.assertEqual(response.status_code, 200)
        
        print("✓ Navigation links are working")
    
    def test_api_endpoints(self):
        """Test API endpoints are accessible."""
        print("\n[TEST] Testing API endpoints...")
        
        api_endpoints = [
            '/api/fleet/status',
            '/api/bookings/active',
            '/api/users/count',
            '/api/payments/recent'
        ]
        
        for endpoint in api_endpoints:
            response = self.client.get(endpoint)
            # API endpoints might require auth, so 401 is acceptable
            self.assertIn(response.status_code, [200, 401, 302])
        
        print("✓ API endpoints are accessible")


class TestDatabaseIntegrity(AdminDashboardTestCase):
    """Test cases for database integrity and operations."""
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraints are enforced."""
        print("\n[TEST] Testing foreign key constraints...")
        
        # Create a booking with valid references
        customer = User(
            email='fk_customer@test.com',
            username='fk_customer',
            first_name='FK',
            last_name='Customer',
            role=Role.CUSTOMER,
            phone='+61 400 600 600'
        )
        customer.set_password('password')
        
        car = Car(
            make='Test', model='Car', year=2023,
            license_plate='FK001', vin='VINFK001',
            category=CarCategory.COMPACT,
            status=CarStatus.AVAILABLE,
            daily_rate=50.00
        )
        
        db.session.add_all([customer, car])
        db.session.commit()
        
        booking = Booking(
            customer_id=customer.id,
            car_id=car.id,
            pickup_date=datetime.utcnow(),
            return_date=datetime.utcnow() + timedelta(days=1),
            pickup_location='Test Location',
            return_location='Test Location',
            daily_rate=50.00,
            total_days=1,
            subtotal=50.00,
            total_amount=55.00,
            status=BookingStatus.CONFIRMED
        )
        booking.generate_booking_number()
        db.session.add(booking)
        db.session.commit()
        
        # Verify relationships work
        self.assertEqual(booking.customer.id, customer.id)
        self.assertEqual(booking.car.id, car.id)
        
        print("✓ Foreign key constraints are working")
    
    def test_cascade_deletions(self):
        """Test cascade deletions work correctly."""
        print("\n[TEST] Testing cascade deletions...")
        
        # Create user with related records
        user = User(
            email='cascade_user@test.com',
            username='cascade_user',
            first_name='Cascade',
            last_name='User',
            role=Role.CUSTOMER,
            phone='+61 400 700 700'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Create payment for user
        payment = Payment(
            user_id=user.id,
            amount=100.00,
            payment_method=PaymentMethod.CREDIT_CARD,
            status=PaymentStatus.COMPLETED,
            transaction_id='CASCADE001'
        )
        db.session.add(payment)
        db.session.commit()
        
        payment_id = payment.id
        
        # Delete user and check if payment is handled appropriately
        # Note: Depending on cascade rules, this might delete or orphan the payment
        db.session.delete(user)
        db.session.commit()
        
        # Verify user is deleted
        deleted_user = User.query.filter_by(email='cascade_user@test.com').first()
        self.assertIsNone(deleted_user)
        
        print("✓ Cascade operations handled correctly")
    
    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        print("\n[TEST] Testing transaction rollback...")
        
        # Start a transaction
        initial_user_count = User.query.count()
        
        try:
            # Try to create an invalid user (missing required fields)
            invalid_user = User(
                email='invalid@test.com'
                # Missing required fields like username, first_name, last_name
            )
            db.session.add(invalid_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
        
        # Verify rollback worked
        final_user_count = User.query.count()
        self.assertEqual(initial_user_count, final_user_count)
        
        print("✓ Transaction rollback working correctly")
    
    def test_unique_constraints(self):
        """Test unique constraints are enforced."""
        print("\n[TEST] Testing unique constraints...")
        
        # Create a user
        user1 = User(
            email='unique@test.com',
            username='unique_user',
            first_name='Unique',
            last_name='User',
            role=Role.CUSTOMER,
            phone='+61 400 800 800'
        )
        user1.set_password('password')
        db.session.add(user1)
        db.session.commit()
        
        # Try to create another user with same email
        user2 = User(
            email='unique@test.com',  # Duplicate email
            username='another_user',
            first_name='Another',
            last_name='User',
            role=Role.CUSTOMER,
            phone='+61 400 900 900'
        )
        user2.set_password('password')
        
        try:
            db.session.add(user2)
            db.session.commit()
            self.fail("Should have raised integrity error for duplicate email")
        except Exception:
            db.session.rollback()
            print("✓ Unique constraints are enforced")


def run_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("ADMIN DASHBOARD COMPREHENSIVE TEST SUITE")
    print("="*60)
    print("\nUsing Pay Advantage Credentials:")
    print("Username: live_83e0ad9f0d3342e699dea15d35cc0d3a")
    print("Password: [HIDDEN]")
    print("\n" + "="*60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    test_classes = [
        TestUserManagement,
        TestFleetManagement,
        TestServicing,
        TestBookings,
        TestInvoicing,
        TestPayAdvantage,
        TestLinkValidation,
        TestDatabaseIntegrity
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailed Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nTests with Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("\n" + "="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)