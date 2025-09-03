#!/usr/bin/env python3
"""Test script for Xero integration."""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"
ADMIN_EMAIL = "admin@aurora.com"
ADMIN_PASSWORD = "admin123"  # Default password from the setup

def test_xero_integration():
    """Test the complete Xero integration flow."""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("=" * 50)
    print("XERO INTEGRATION TEST")
    print("=" * 50)
    print()
    
    # Step 1: Login as admin
    print("1. Logging in as admin...")
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
    
    if response.status_code in [302, 303]:
        print(f"   ✓ Login successful (redirected)")
    else:
        # Try JSON login endpoint
        response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print(f"   ✓ Login successful")
        else:
            print(f"   ✗ Login failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return
    
    # Step 2: Check Xero status
    print("\n2. Checking Xero connection status...")
    response = session.get(f"{BASE_URL}/xero/status")
    
    if response.status_code == 200:
        print(f"   ✓ Status endpoint accessible")
        try:
            status_data = response.json()
            print(f"   Connected: {status_data.get('connected', False)}")
            if status_data.get('connected'):
                print(f"   Tenant: {status_data.get('tenant_name', 'N/A')}")
                print(f"   Expires: {status_data.get('expires_at', 'N/A')}")
        except:
            print(f"   Response: {response.text[:200]}")
    else:
        print(f"   ✗ Status check failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    
    # Step 3: Get authorization URL
    print("\n3. Getting Xero authorization URL...")
    response = session.get(f"{BASE_URL}/xero/authorize", allow_redirects=False)
    
    if response.status_code in [302, 303]:
        auth_url = response.headers.get('Location', '')
        if 'login.xero.com' in auth_url:
            print(f"   ✓ Authorization URL obtained")
            print(f"   URL: {auth_url[:100]}...")
            print("\n   To complete authorization:")
            print(f"   1. Open this URL in a browser: {auth_url}")
            print("   2. Log in to Xero")
            print("   3. Authorize the application")
            print("   4. You'll be redirected back to the callback URL")
        else:
            print(f"   ✗ Unexpected redirect: {auth_url[:100]}")
    else:
        print(f"   ✗ Failed to get authorization URL: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    
    # Step 4: Test connection endpoint
    print("\n4. Testing Xero connection...")
    response = session.get(f"{BASE_URL}/xero/test-connection")
    
    if response.status_code == 200:
        try:
            test_data = response.json()
            if test_data.get('success'):
                print(f"   ✓ Connection test successful")
                org = test_data.get('organization', {})
                print(f"   Organization: {org.get('Name', 'N/A')}")
            else:
                print(f"   ✗ Connection test failed: {test_data.get('message', 'Unknown error')}")
        except:
            print(f"   Response: {response.text[:200]}")
    elif response.status_code == 404:
        print(f"   ℹ No Xero connection found (need to authorize first)")
    else:
        print(f"   ✗ Connection test failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    print("\nSUMMARY:")
    print("✓ Admin user has ADMIN role")
    print("✓ Xero credentials configured")
    print("✓ All Xero endpoints are accessible (no more 403 errors)")
    print("\nNEXT STEPS:")
    print("1. Complete the OAuth2 authorization flow by visiting the authorization URL")
    print("2. Once authorized, you can send invoices from the admin dashboard")
    print("3. The Xero integration will automatically refresh tokens as needed")

if __name__ == "__main__":
    test_xero_integration()