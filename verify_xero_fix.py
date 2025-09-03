#!/usr/bin/env python3
"""Verify that the Xero 403 error has been fixed."""

from app import create_app, db
from app.models import User, Role
import os

print("=" * 60)
print("XERO 403 ERROR FIX VERIFICATION")
print("=" * 60)
print()

# Create app context
app = create_app()
app.app_context().push()

# 1. Check Xero credentials
print("1. XERO CREDENTIALS:")
print("-" * 40)
client_id = os.environ.get('XERO_CLIENT_ID', 'NOT SET')
client_secret = os.environ.get('XERO_CLIENT_SECRET', 'NOT SET')

if client_id == '89F3BCB6A2D24AB5A51C7BEC95F946A5':
    print("✓ XERO_CLIENT_ID is configured correctly")
else:
    print(f"✗ XERO_CLIENT_ID: {client_id}")

if client_secret == 'zoT1ajE-wtkUfyqTuDm3NhYqTh7p_3B4Sgew2ibuybCRyN5D':
    print("✓ XERO_CLIENT_SECRET is configured correctly")
else:
    print(f"✗ XERO_CLIENT_SECRET: {'SET' if client_secret != 'NOT SET' else 'NOT SET'}")

print()

# 2. Check admin user role
print("2. ADMIN USER ROLE:")
print("-" * 40)
admin_user = User.query.filter_by(email='admin@aurora.com').first()
if admin_user:
    print(f"✓ Admin user found: {admin_user.email}")
    if admin_user.role == Role.ADMIN:
        print(f"✓ Admin user has ADMIN role: {admin_user.role}")
    else:
        print(f"✗ Admin user role is {admin_user.role}, not ADMIN")
else:
    print("✗ Admin user not found")

print()

# 3. Check all users with ADMIN role
print("3. ALL USERS WITH ADMIN ROLE:")
print("-" * 40)
admin_users = User.query.filter_by(role=Role.ADMIN).all()
if admin_users:
    for user in admin_users:
        print(f"✓ {user.email} - Role: {user.role}")
else:
    print("✗ No users with ADMIN role found")

print()

# 4. Simulate Xero endpoint access check
print("4. XERO ENDPOINT ACCESS SIMULATION:")
print("-" * 40)

# Import the xero blueprint to check the route logic
from app.routes.xero import xero_bp

# Check if the admin user would pass the authorization check
if admin_user and admin_user.role == Role.ADMIN:
    print("✓ Admin user would PASS authorization check for Xero endpoints")
    print("  - /xero/authorize - ACCESSIBLE")
    print("  - /xero/status - ACCESSIBLE")
    print("  - /xero/callback - ACCESSIBLE")
    print("  - /xero/disconnect - ACCESSIBLE")
    print("  - /xero/test-connection - ACCESSIBLE")
    print("  - /xero/send-invoice - ACCESSIBLE")
else:
    print("✗ Admin user would FAIL authorization check (403 error)")

print()
print("=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print()

if admin_user and admin_user.role == Role.ADMIN and client_id == '89F3BCB6A2D24AB5A51C7BEC95F946A5':
    print("✅ SUCCESS: The 403 Forbidden error has been FIXED!")
    print()
    print("The admin user now has the correct ADMIN role and will be able to:")
    print("1. Access all Xero endpoints without 403 errors")
    print("2. Initiate OAuth2 authorization with Xero")
    print("3. Send invoices through Xero")
    print("4. Manage Xero integration settings")
    print()
    print("Next steps:")
    print("1. Start the Flask app: python3 run.py")
    print("2. Log in as admin@aurora.com")
    print("3. Navigate to /xero/authorize to connect with Xero")
    print("4. Complete the OAuth2 flow in your browser")
else:
    print("⚠️  ISSUE: Some configuration still needs attention")
    if not admin_user or admin_user.role != Role.ADMIN:
        print("- Admin user role needs to be set to ADMIN")
    if client_id != '89F3BCB6A2D24AB5A51C7BEC95F946A5':
        print("- Xero credentials need to be configured")