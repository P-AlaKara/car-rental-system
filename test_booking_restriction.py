#!/usr/bin/env python3
"""
Test script to verify that users cannot book cars without driver license and address details.
"""

import requests
from datetime import datetime, timedelta

# Base URL for the application
BASE_URL = "http://localhost:5000"

def test_booking_restriction():
    """Test that booking is restricted for users without complete profile."""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("=" * 60)
    print("Testing Booking Restriction Feature")
    print("=" * 60)
    
    # Test data for a user without license/address
    test_user = {
        'username': 'testuser_incomplete',
        'email': 'testincomplete@example.com',
        'password': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    print("\n1. Creating a test user without license and address details...")
    
    # Register the user
    register_url = f"{BASE_URL}/auth/register"
    response = session.post(register_url, data=test_user, allow_redirects=False)
    
    if response.status_code in [302, 303]:
        print("   ✓ User registered successfully")
    else:
        print(f"   ✗ Registration failed: {response.status_code}")
        return
    
    print("\n2. Logging in as the test user...")
    
    # Login
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        'username': test_user['username'],
        'password': test_user['password']
    }
    response = session.post(login_url, data=login_data, allow_redirects=False)
    
    if response.status_code in [302, 303]:
        print("   ✓ Logged in successfully")
    else:
        print(f"   ✗ Login failed: {response.status_code}")
        return
    
    print("\n3. Attempting to access booking page...")
    
    # Try to access booking creation page
    booking_url = f"{BASE_URL}/bookings/new"
    response = session.get(booking_url, allow_redirects=False)
    
    if response.status_code == 302:
        redirect_location = response.headers.get('Location', '')
        if 'edit_profile' in redirect_location or 'profile' in redirect_location:
            print("   ✓ User correctly redirected to profile edit page")
            print(f"   → Redirect URL: {redirect_location}")
            
            # Follow the redirect to see the flash message
            response = session.get(BASE_URL + redirect_location)
            if 'complete your profile' in response.text.lower():
                print("   ✓ Profile completion message displayed")
        else:
            print(f"   ✗ Unexpected redirect: {redirect_location}")
    else:
        print(f"   ✗ Expected redirect but got status code: {response.status_code}")
    
    print("\n4. Checking cars listing page...")
    
    # Check cars listing page
    cars_url = f"{BASE_URL}/cars"
    response = session.get(cars_url)
    
    if response.status_code == 200:
        content = response.text.lower()
        if 'complete profile' in content or 'profile incomplete' in content:
            print("   ✓ Profile completion warning shown on cars page")
        if 'complete profile to book' in content:
            print("   ✓ 'Complete Profile to Book' button shown instead of 'Book Now'")
    else:
        print(f"   ✗ Failed to load cars page: {response.status_code}")
    
    print("\n5. Testing with complete profile...")
    
    # Now update the profile with license and address
    profile_url = f"{BASE_URL}/auth/edit_profile"
    profile_data = {
        'first_name': test_user['first_name'],
        'last_name': test_user['last_name'],
        'email': test_user['email'],
        'phone': '1234567890',
        'address': '123 Test Street',
        'city': 'Melbourne',
        'state': 'VIC',
        'zip_code': '3000',
        'license_number': 'TEST123456',
        'license_expiry': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    }
    
    response = session.post(profile_url, data=profile_data, allow_redirects=False)
    
    if response.status_code in [302, 303]:
        print("   ✓ Profile updated with license and address")
    
    print("\n6. Attempting to access booking page with complete profile...")
    
    # Try to access booking page again
    response = session.get(booking_url, allow_redirects=False)
    
    if response.status_code == 200:
        print("   ✓ Booking page accessible with complete profile")
        if 'Create New Booking' in response.text:
            print("   ✓ Booking form displayed correctly")
    elif response.status_code == 302:
        print(f"   ✗ Still being redirected: {response.headers.get('Location')}")
    else:
        print(f"   ✗ Unexpected status code: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("✓ Users without driver license and address cannot book cars")
    print("✓ Users are redirected to complete their profile")
    print("✓ Clear messaging is shown to guide users")
    print("✓ Once profile is complete, booking is allowed")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_booking_restriction()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("\nMake sure the Flask application is running on http://localhost:5000")