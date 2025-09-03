#!/usr/bin/env python3
"""
Test script to verify the vehicle return implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_models():
    """Test if models are properly defined"""
    print("Testing models...")
    try:
        from app.models import VehicleReturn, Booking, BookingStatus, Car, CarStatus
        print("✅ VehicleReturn model imported successfully")
        
        # Check VehicleReturn attributes
        required_attrs = [
            'bond_returned', 'all_payments_received', 
            'car_in_good_condition', 'fuel_tank_full',
            'odometer_reading', 'calculate_total_charges',
            'is_checklist_complete'
        ]
        
        for attr in required_attrs:
            if not hasattr(VehicleReturn, attr):
                print(f"❌ Missing attribute: {attr}")
                return False
        
        print("✅ All required attributes found in VehicleReturn model")
        return True
    except ImportError as e:
        print(f"❌ Error importing models: {e}")
        return False

def test_routes():
    """Test if routes are properly defined"""
    print("\nTesting routes...")
    try:
        from app.routes import bookings
        
        # Check if new routes exist
        route_functions = ['process_return', 'view_return', 'start']
        
        for func_name in route_functions:
            if not hasattr(bookings, func_name):
                print(f"❌ Missing route function: {func_name}")
                return False
        
        print("✅ All required route functions found")
        return True
    except ImportError as e:
        print(f"❌ Error importing routes: {e}")
        return False

def test_templates():
    """Test if templates exist"""
    print("\nTesting templates...")
    templates = [
        'templates/pages/bookings/return.html',
        'templates/pages/bookings/return_view.html'
    ]
    
    all_exist = True
    for template in templates:
        if os.path.exists(template):
            print(f"✅ Template exists: {template}")
        else:
            print(f"❌ Template missing: {template}")
            all_exist = False
    
    return all_exist

def test_database():
    """Test database table creation"""
    print("\nTesting database...")
    import sqlite3
    
    try:
        conn = sqlite3.connect('instance/car_rental.db')
        cursor = conn.cursor()
        
        # Check if vehicle_returns table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='vehicle_returns'
        """)
        
        if cursor.fetchone():
            print("✅ vehicle_returns table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(vehicle_returns)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = [
                'id', 'booking_id', 'bond_returned', 
                'all_payments_received', 'car_in_good_condition',
                'fuel_tank_full', 'odometer_reading'
            ]
            
            for col in required_columns:
                if col in column_names:
                    print(f"  ✅ Column exists: {col}")
                else:
                    print(f"  ❌ Column missing: {col}")
            
            conn.close()
            return True
        else:
            print("❌ vehicle_returns table does not exist")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("VEHICLE RETURN IMPLEMENTATION TEST")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Models", test_models()))
    results.append(("Routes", test_routes()))
    results.append(("Templates", test_templates()))
    results.append(("Database", test_database()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Vehicle return process is ready to use.")
        print("\nHow to use:")
        print("1. Manager confirms a booking")
        print("2. Manager clicks 'Start Rental' when customer picks up the vehicle")
        print("3. When customer returns, manager clicks 'Process Return'")
        print("4. Manager fills out the checklist:")
        print("   - Bond returned (yes/no)")
        print("   - All payments received (yes/no)")
        print("   - Car in good condition (yes/no)")
        print("   - Fuel tank full (yes/no)")
        print("   - Enter odometer reading")
        print("   - Add any additional charges if needed")
        print("5. Submit to complete the return")
        print("6. Booking status changes to 'completed'")
        print("7. Car becomes available for booking again")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)