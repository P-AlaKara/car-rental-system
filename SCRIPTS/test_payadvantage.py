import os
from datetime import datetime, timedelta, date

from app import create_app, db
from app.models import User, Role
from app.models.car import Car, CarCategory, CarStatus
from app.models.booking import Booking, BookingStatus
from app.models.pay_advantage import PayAdvantageCustomer
from app.services.pay_advantage import PayAdvantageService


def ensure_database_initialized():
    db.create_all()


def ensure_minimum_car() -> Car:
    car = Car.query.first()
    if car:
        return car
    car = Car(
        make='Toyota',
        model='Corolla',
        year=2022,
        category=CarCategory.COMPACT,
        license_plate='TEST1234',
        vin='VINTEST123456',
        seats=5,
        transmission='Automatic',
        fuel_type='Gasoline',
        daily_rate=50.0,
        status=CarStatus.AVAILABLE,
        color='White',
        mileage=10000,
        agency='aurora motors'
    )
    db.session.add(car)
    db.session.commit()
    return car


def ensure_user(email: str, first_name: str, last_name: str, phone: str) -> User:
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(
        email=email,
        username=email.split('@')[0],
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=Role.CUSTOMER,
        is_active=True,
        is_verified=True,
        address='1 Test Street',
        city='Melbourne',
        state='VIC',
        zip_code='3000',
        country='Australia'
    )
    user.set_password('TempPass123!')
    db.session.add(user)
    db.session.commit()
    return user


def ensure_booking(user: User, car: Car) -> Booking:
    booking = Booking.query.filter_by(customer_id=user.id, car_id=car.id).first()
    if booking:
        return booking
    pickup_date = datetime.utcnow() + timedelta(days=1)
    return_date = pickup_date + timedelta(days=3)
    booking = Booking(
        booking_number=f"BK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        customer_id=user.id,
        car_id=car.id,
        pickup_date=pickup_date,
        return_date=return_date,
        pickup_location='Melbourne CBD',
        return_location='Melbourne CBD',
        daily_rate=car.daily_rate,
        total_days=3,
        subtotal=car.daily_rate * 3,
        tax_amount=0,
        discount_amount=0,
        additional_charges=0,
        total_amount=car.daily_rate * 3,
        deposit_amount=0,
        status=BookingStatus.CONFIRMED,
        with_driver=False,
        insurance_opted=False
    )
    db.session.add(booking)
    db.session.commit()
    return booking


def main():
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    with app.app_context():
        ensure_database_initialized()

        # Set Pay Advantage credentials from env
        pa_username = os.environ.get('PAY_ADVANTAGE_USERNAME')
        pa_password = os.environ.get('PAY_ADVANTAGE_PASSWORD')
        if not pa_username or not pa_password:
            raise RuntimeError('PAY_ADVANTAGE_USERNAME and PAY_ADVANTAGE_PASSWORD must be set in environment')

        # User details from request
        first_name = 'Priscilla'
        last_name = 'Customer'
        email = 'alakara101@gmail.com'
        phone = '+61430011219'

        user = ensure_user(email=email, first_name=first_name, last_name=last_name, phone=phone)
        car = ensure_minimum_car()
        booking = ensure_booking(user=user, car=car)

        pa_service = PayAdvantageService()
        pa_customer = pa_service.get_or_create_customer(user)

        # Create a minimal direct debit schedule to get authorization URL
        today = date.today()
        schedule_info = pa_service.create_direct_debit_schedule(
            booking_id=booking.id,
            customer_code=pa_customer.customer_code,
            description=f"Booking {booking.booking_number} Direct Debit Authorization",
            upfront_amount=None,
            upfront_date=None,
            recurring_amount=booking.total_amount,
            recurring_start_date=today + timedelta(days=7),
            frequency='monthly',
            end_condition_amount=booking.total_amount,
            reminder_days=2
        )

        print("\nPay Advantage Setup Complete:")
        print(f"  Customer Code: {pa_customer.customer_code}")
        print(f"  DDR Authorization URL: {schedule_info.get('authorization_url')}")


if __name__ == '__main__':
    main()