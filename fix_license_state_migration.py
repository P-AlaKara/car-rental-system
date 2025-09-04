#!/usr/bin/env python3
"""
Migration script to fix users who have state set but license_state not set.
This ensures users can book cars without issues.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def fix_license_states():
    """Fix users who have state but no license_state"""
    app = create_app()
    
    with app.app_context():
        # Find all users with state but no license_state
        users_to_fix = User.query.filter(
            User.state.isnot(None),
            User.license_state.is_(None)
        ).all()
        
        if not users_to_fix:
            print("✅ No users need fixing - all users with state also have license_state")
            return 0
        
        print(f"Found {len(users_to_fix)} users with state but no license_state")
        print("\nFixing users:")
        
        fixed_count = 0
        for user in users_to_fix:
            # Only fix if they have a license number (indicating they're trying to use driver features)
            if user.license_number:
                print(f"  - {user.email}: Setting license_state to '{user.state}'")
                user.license_state = user.state
                fixed_count += 1
            else:
                print(f"  - {user.email}: Skipping (no license number)")
        
        if fixed_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully fixed {fixed_count} users")
        else:
            print("\n✅ No users needed fixing (none had license numbers)")
        
        # Verify the fix
        remaining = User.query.filter(
            User.state.isnot(None),
            User.license_state.is_(None),
            User.license_number.isnot(None)
        ).count()
        
        if remaining > 0:
            print(f"⚠️  Warning: {remaining} users still have issues")
            return 1
        else:
            print("✅ All users with license numbers now have license_state set")
            return 0

if __name__ == "__main__":
    exit_code = fix_license_states()
    sys.exit(exit_code)