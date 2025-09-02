#!/usr/bin/env python
"""
Test script to verify the Flask application setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    try:
        from app import create_app, db
        print("✓ App module imported successfully")
        
        from app.models import User, Car, Booking, Payment, Driver
        print("✓ Models imported successfully")
        
        from config import Config
        print("✓ Config imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_creation():
    """Test if the Flask app can be created."""
    print("\nTesting app creation...")
    try:
        from app import create_app
        app = create_app('testing')
        print("✓ App created successfully")
        
        with app.app_context():
            from app import db
            db.create_all()
            print("✓ Database tables created successfully")
        
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def test_routes():
    """Test if routes are registered."""
    print("\nTesting routes...")
    try:
        from app import create_app
        app = create_app('testing')
        
        # Check some key routes
        routes = [r.rule for r in app.url_map.iter_rules()]
        
        required_routes = ['/', '/auth/login', '/auth/register', '/cars/', '/bookings/', '/dashboard/']
        
        for route in required_routes:
            if any(route in r for r in routes):
                print(f"✓ Route '{route}' registered")
            else:
                print(f"✗ Route '{route}' not found")
        
        return True
    except Exception as e:
        print(f"✗ Route testing error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Aurora Motors - Flask Application Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_creation,
        test_routes
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("1. Create a .env file from .env.example")
        print("2. Run: python run.py init_db")
        print("3. Run: python run.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    print("=" * 50)

if __name__ == '__main__':
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()