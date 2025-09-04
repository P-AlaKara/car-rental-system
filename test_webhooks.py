import os
import json
import hmac
import hashlib
from datetime import datetime, timedelta, date

from app import create_app, db
from app.models import User
from app.models.car import Car, CarCategory, CarStatus
from app.models.booking import Booking, BookingStatus


def _hmac_header(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode('utf-8'), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def setup_app_and_db():
    app = create_app('testing')
    app.config['PAY_ADVANTAGE_WEBHOOK_SECRET'] = 'test_secret'
    with app.app_context():
        db.create_all()
    return app


def seed_booking(app):
    with app.app_context():
        user = User(email='cust@example.com', username='cust', first_name='Test', last_name='User')
        user.set_password('pass')
        db.session.add(user)

        car = Car(
            make='Test', model='Car', year=2024,
            license_plate='TEST123', vin='VIN123456',
            category=CarCategory.MIDSIZE, seats=5,
            daily_rate=100.0, status=CarStatus.AVAILABLE
        )
        db.session.add(car)
        db.session.commit()

        booking = Booking(
            booking_number='BKTEST',
            customer_id=user.id,
            car_id=car.id,
            pickup_date=datetime.utcnow(),
            return_date=datetime.utcnow() + timedelta(days=3),
            pickup_location='A',
            return_location='A',
            daily_rate=100.0,
            total_days=3,
            subtotal=300.0,
            total_amount=300.0,
            status=BookingStatus.PENDING
        )
        db.session.add(booking)
        db.session.commit()
        return booking.id


def test_webhook_rejects_missing_signature():
    app = setup_app_and_db()
    client = app.test_client()
    resp = client.post('/webhooks/payadvantage', data=b'{}', headers={'Content-Type': 'application/json'})
    assert resp.status_code == 401


def test_webhook_accepts_valid_signature_and_creates_payment():
    app = setup_app_and_db()
    booking_id = seed_booking(app)
    client = app.test_client()

    payload = {
        'scheduleId': 'sched_1',
        'paymentId': 'pay_1',
        'bookingId': booking_id,
        'PaidDate': date.today().isoformat(),
        'PaidAmount': 100.0,
        'status': 'completed'
    }
    body = json.dumps(payload).encode('utf-8')
    sig = _hmac_header(app.config['PAY_ADVANTAGE_WEBHOOK_SECRET'], body)

    resp = client.post('/webhooks/payadvantage', data=body, headers={
        'Content-Type': 'application/json',
        'X-PayAdvantage-Signature': sig
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True

    with app.app_context():
        from app.models import Payment
        p = Payment.query.filter_by(booking_id=booking_id, gateway_transaction_id='pay_1').first()
        assert p is not None
        assert p.amount == 100.0
        # Booking should be confirmed
        b = Booking.query.get(booking_id)
        assert b.status == BookingStatus.CONFIRMED


def test_webhook_idempotency_duplicate_event():
    app = setup_app_and_db()
    booking_id = seed_booking(app)
    client = app.test_client()

    payload = {
        'scheduleId': 'sched_2',
        'paymentId': 'pay_2',
        'bookingId': booking_id,
        'PaidDate': date.today().isoformat(),
        'PaidAmount': 150.0,
        'status': 'completed'
    }
    body = json.dumps(payload).encode('utf-8')
    sig = _hmac_header(app.config['PAY_ADVANTAGE_WEBHOOK_SECRET'], body)

    for _ in range(2):
        resp = client.post('/webhooks/payadvantage', data=body, headers={
            'Content-Type': 'application/json',
            'X-PayAdvantage-Signature': sig
        })
        assert resp.status_code == 200

    with app.app_context():
        from app.models import Payment
        payments = Payment.query.filter_by(booking_id=booking_id, gateway_transaction_id='pay_2').all()
        assert len(payments) == 1

