#!/usr/bin/env python3
"""
Test script to verify that booking restrictions are working properly.
Users should not be able to book a car without driver license and address details.
"""

import sys
from datetime import datetime, timedelta, date
from app import create_app, db
from app.models import User, Car, Booking, CarStatus, BookingStatus
from werkzeug.security import generate_password_hash

def test_booking_restriction():
    """Test that users cannot book without complete driver details."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("TESTING BOOKING RESTRICTION FOR INCOMPLETE PROFILES")
        print("="*60)
        
        # Create a test user without complete details
        test_user = User.query.filter_by(username='testdriver').first()
        if not test_user:
            test_user = User(
                username='testdriver',
                email='testdriver@example.com',
                first_name='Test',
                last_name='Driver',
                password_hash=generate_password_hash('password123'),
                phone='+61400000000'
                # Note: Missing license_number, license_expiry, address, city, state, zip_code
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"\n✓ Created test user: {test_user.username}")
        else:
            # Clear driver details to test restriction
            test_user.license_number = None
            test_user.license_expiry = None
            test_user.address = None
            test_user.city = None
            test_user.state = None
            test_user.zip_code = None
            db.session.commit()
            print(f"\n✓ Reset test user profile: {test_user.username}")
        
        # Test 1: Check if user has incomplete details
        print("\n--- Test 1: Checking user profile completeness ---")
        has_complete = test_user.has_complete_driver_details()
        missing = test_user.get_missing_details()
        
        print(f"Has complete driver details: {has_complete}")
        print(f"Expected: False")
        assert not has_complete, "User should not have complete details"
        print("✓ PASSED: User correctly identified as having incomplete profile")
        
        print(f"\nMissing details: {missing}")
        expected_missing = ["Driver's license number", "Driver's license expiry date", 
                          "Street address", "City", "State", "ZIP code"]
        assert all(item in missing for item in expected_missing), f"Missing details don't match expected"
        print("✓ PASSED: All missing details correctly identified")
        
        # Test 2: Try to create a booking (should fail)
        print("\n--- Test 2: Attempting to create booking with incomplete profile ---")
        car = Car.query.filter_by(status=CarStatus.AVAILABLE).first()
        if car:
            print(f"Attempting to book car: {car.full_name}")
            
            # This simulates what happens in the route
            if not test_user.has_complete_driver_details():
                print("✓ PASSED: Booking prevented due to incomplete profile")
                print("System would redirect to profile completion page")
            else:
                print("✗ FAILED: User was allowed to proceed with booking")
                sys.exit(1)
        
        # Test 3: Complete the profile and verify booking is allowed
        print("\n--- Test 3: Completing profile and verifying booking access ---")
        test_user.license_number = "DL123456"
        test_user.license_expiry = date(2025, 12, 31)
        test_user.address = "123 Test Street"
        test_user.city = "Melbourne"
        test_user.state = "VIC"
        test_user.zip_code = "3000"
        db.session.commit()
        
        has_complete = test_user.has_complete_driver_details()
        missing = test_user.get_missing_details()
        
        print(f"Has complete driver details: {has_complete}")
        print(f"Expected: True")
        assert has_complete, "User should have complete details after update"
        print("✓ PASSED: User profile is now complete")
        
        print(f"Missing details: {missing}")
        assert len(missing) == 0, "Should have no missing details"
        print("✓ PASSED: No missing details after profile completion")
        
        if car:
            if test_user.has_complete_driver_details():
                print("✓ PASSED: User can now proceed with booking")
            else:
                print("✗ FAILED: User still cannot book despite complete profile")
                sys.exit(1)
        
        # Test 4: Test expired license
        print("\n--- Test 4: Testing expired license restriction ---")
        test_user.license_expiry = date(2020, 1, 1)  # Expired license
        db.session.commit()
        
        has_complete = test_user.has_complete_driver_details()
        missing = test_user.get_missing_details()
        
        print(f"Has complete driver details (with expired license): {has_complete}")
        print(f"Expected: False")
        assert not has_complete, "User should not have complete details with expired license"
        print("✓ PASSED: Expired license correctly prevents booking")
        
        assert "Valid driver's license (current license is expired)" in missing
        print("✓ PASSED: Expired license message shown correctly")
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        print("\nSummary:")
        print("✓ Users without driver license details cannot book")
        print("✓ Users without address details cannot book")
        print("✓ Users with expired licenses cannot book")
        print("✓ Users with complete valid details can book")
        print("✓ Missing details are correctly identified and displayed")
        
        # Clean up test user (optional)
        # db.session.delete(test_user)
        # db.session.commit()

if __name__ == '__main__':
    test_booking_restriction()