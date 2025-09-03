#!/usr/bin/env python
"""
Aurora Motors - Car Rental Management System
Main application entry point
"""

import os
from app import create_app, db
from app.models import User, Role

# Get environment from environment variable
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)


@app.shell_context_processor
def make_shell_context():
    """Make database models available in flask shell."""
    return {
        'db': db,
        'User': User,
        'Role': Role
    }


@app.cli.command()
def init_db():
    """Initialize the database with tables and default data."""
    db.create_all()
    print("Database tables created.")
    
    # Create default admin user if not exists
    admin = User.query.filter_by(email='admin@auroramotors.com').first()
    if not admin:
        admin = User(
            email='admin@auroramotors.com',
            username='admin',
            first_name='System',
            last_name='Administrator',
            role=Role.ADMIN,
            is_active=True,
            is_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created:")
        print("  Email: admin@auroramotors.com")
        print("  Password: admin123")
        print("  Please change the password after first login!")


@app.cli.command()
def list_users():
    """List all users in the database."""
    users = User.query.all()
    
    if not users:
        print("\n❌ No users found in the database.")
        return
    
    print("\n" + "=" * 80)
    print("USERS IN DATABASE")
    print("=" * 80)
    print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<15} {'Active':<8}")
    print("-" * 80)
    
    for user in users:
        role_value = user.role.value if user.role else 'None'
        print(f"{user.id:<5} {user.username:<20} {user.email:<30} {role_value:<15} {'Yes' if user.is_active else 'No':<8}")
    
    print("\n" + "=" * 80)


@app.cli.command()
def make_admin():
    """Make a user an admin by email or ID."""
    import click
    
    users = User.query.all()
    if not users:
        print("❌ No users found in the database.")
        return
    
    print("\nCurrent users:")
    for user in users:
        role_value = user.role.value if user.role else 'None'
        print(f"  ID: {user.id} - {user.email} ({role_value})")
    
    user_input = click.prompt('\nEnter user email or ID to make admin')
    
    # Try to find by ID first
    try:
        user_id = int(user_input)
        user = User.query.get(user_id)
    except ValueError:
        # Try to find by email
        user = User.query.filter_by(email=user_input).first()
    
    if not user:
        print(f"❌ User '{user_input}' not found.")
        return
    
    if user.role == Role.ADMIN:
        print(f"ℹ️  User '{user.email}' is already an admin.")
        return
    
    user.role = Role.ADMIN
    db.session.commit()
    print(f"✅ Successfully updated user '{user.email}' to ADMIN role!")


@app.cli.command()
def make_all_admin():
    """Make all users admins (for development only)."""
    import click
    
    if not click.confirm('\n⚠️  This will make ALL users admins. Continue?'):
        print("Operation cancelled.")
        return
    
    users = User.query.filter(User.role != Role.ADMIN).all()
    
    if not users:
        print("ℹ️  All users are already admins.")
        return
    
    for user in users:
        user.role = Role.ADMIN
    
    db.session.commit()
    print(f"✅ Successfully updated {len(users)} user(s) to ADMIN role!")


@app.cli.command()
def seed_db():
    """Seed the database with sample data."""
    from datetime import datetime, timedelta
    from app.models import Car, CarCategory, CarStatus
    import random
    
    # Sample car data
    cars_data = [
        {'make': 'Toyota', 'model': 'Camry', 'year': 2023, 'category': CarCategory.MIDSIZE},
        {'make': 'Honda', 'model': 'Civic', 'year': 2023, 'category': CarCategory.COMPACT},
        {'make': 'Ford', 'model': 'Mustang', 'year': 2023, 'category': CarCategory.SPORTS},
        {'make': 'Chevrolet', 'model': 'Tahoe', 'year': 2023, 'category': CarCategory.SUV},
        {'make': 'Tesla', 'model': 'Model 3', 'year': 2023, 'category': CarCategory.ELECTRIC},
        {'make': 'BMW', 'model': '5 Series', 'year': 2023, 'category': CarCategory.LUXURY},
        {'make': 'Mercedes-Benz', 'model': 'E-Class', 'year': 2023, 'category': CarCategory.LUXURY},
        {'make': 'Nissan', 'model': 'Altima', 'year': 2023, 'category': CarCategory.MIDSIZE},
        {'make': 'Hyundai', 'model': 'Elantra', 'year': 2023, 'category': CarCategory.COMPACT},
        {'make': 'Jeep', 'model': 'Wrangler', 'year': 2023, 'category': CarCategory.SUV},
    ]
    
    for car_data in cars_data:
        # Check if car already exists
        existing = Car.query.filter_by(
            make=car_data['make'],
            model=car_data['model'],
            year=car_data['year']
        ).first()
        
        if not existing:
            car = Car(
                make=car_data['make'],
                model=car_data['model'],
                year=car_data['year'],
                category=car_data['category'],
                license_plate=f"ABC{random.randint(1000, 9999)}",
                vin=f"VIN{random.randint(100000, 999999)}",
                seats=random.choice([2, 4, 5, 7]),
                transmission='Automatic',
                fuel_type='Electric' if car_data['category'] == CarCategory.ELECTRIC else 'Gasoline',
                daily_rate=random.randint(50, 200),
                status=CarStatus.AVAILABLE,
                color=random.choice(['Black', 'White', 'Silver', 'Blue', 'Red']),
                mileage=random.randint(1000, 50000),
                agency=random.choice(['smart', 'rehema enterprise', 'aurora motors', 'JIN'])
            )
            
            # Set weekly and monthly rates
            car.weekly_rate = car.daily_rate * 6.5
            car.monthly_rate = car.daily_rate * 25
            
            # Add features
            car.features = ['GPS', 'Bluetooth', 'Backup Camera', 'Cruise Control']
            
            # Add sample images (using placeholder URLs for demo)
            car.images = [
                f"https://via.placeholder.com/800x600/888888/FFFFFF?text={car_data['make']}+{car_data['model']}+1",
                f"https://via.placeholder.com/800x600/666666/FFFFFF?text={car_data['make']}+{car_data['model']}+2",
                f"https://via.placeholder.com/800x600/444444/FFFFFF?text={car_data['make']}+{car_data['model']}+3"
            ]
            
            db.session.add(car)
    
    db.session.commit()
    print(f"Sample cars added to database.")
    
    # Create sample customers
    for i in range(1, 6):
        email = f"customer{i}@example.com"
        if not User.query.filter_by(email=email).first():
            customer = User(
                email=email,
                username=f"customer{i}",
                first_name=f"Customer",
                last_name=f"{i}",
                phone=f"555-000{i}",
                role=Role.CUSTOMER,
                is_active=True,
                is_verified=True
            )
            customer.set_password('password123')
            db.session.add(customer)
    
    db.session.commit()
    print("Sample customers added to database.")


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )