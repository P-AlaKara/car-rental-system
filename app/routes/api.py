from flask import Blueprint, jsonify, request
from app import db
from app.models import User, Car, Booking, Payment, Driver
from app.routes.auth import verify_token
from functools import wraps

api_bp = Blueprint('api', __name__)


def token_required(f):
    """Decorator to require valid JWT token for API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        request.current_user_id = payload['user_id']
        request.current_user_role = payload['role']
        return f(*args, **kwargs)
    
    return decorated


@api_bp.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Aurora Motors API',
        'version': '1.0.0'
    })


# User endpoints
@api_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """Get all users (admin only)."""
    if request.current_user_role not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@api_bp.route('/users/<int:id>', methods=['GET'])
@token_required
def get_user(id):
    """Get user by ID."""
    if request.current_user_role not in ['admin', 'manager'] and request.current_user_id != id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())


@api_bp.route('/users/<int:id>', methods=['PUT'])
@token_required
def update_user(id):
    """Update user details."""
    if request.current_user_id != id and request.current_user_role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    # Update allowed fields
    updateable_fields = ['first_name', 'last_name', 'phone', 'address', 
                        'city', 'state', 'zip_code']
    
    for field in updateable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    return jsonify(user.to_dict())


# Car endpoints
@api_bp.route('/cars', methods=['GET'])
def get_cars():
    """Get all available cars."""
    category = request.args.get('category')
    available_only = request.args.get('available', 'true').lower() == 'true'
    
    query = Car.query
    
    if category:
        query = query.filter_by(category=category)
    if available_only:
        query = query.filter_by(status='available', is_active=True)
    
    cars = query.all()
    return jsonify([car.to_dict() for car in cars])


@api_bp.route('/cars/<int:id>', methods=['GET'])
def get_car(id):
    """Get car by ID."""
    car = Car.query.get_or_404(id)
    return jsonify(car.to_dict())


@api_bp.route('/cars/<int:id>/availability', methods=['GET'])
def check_car_availability(id):
    """Check car availability for specific dates."""
    car = Car.query.get_or_404(id)
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start and end dates required'}), 400
    
    # Check for overlapping bookings
    overlapping = Booking.query.filter(
        Booking.car_id == car.id,
        Booking.status.in_(['confirmed', 'in_progress']),
        db.or_(
            db.and_(
                Booking.pickup_date <= start_date,
                Booking.return_date >= start_date
            ),
            db.and_(
                Booking.pickup_date <= end_date,
                Booking.return_date >= end_date
            )
        )
    ).count()
    
    available = overlapping == 0 and car.is_available
    
    return jsonify({
        'available': available,
        'car_id': car.id,
        'car_name': car.full_name,
        'daily_rate': car.daily_rate
    })


# Booking endpoints
@api_bp.route('/bookings', methods=['GET'])
@token_required
def get_bookings():
    """Get bookings for current user or all bookings (admin)."""
    if request.current_user_role in ['admin', 'manager']:
        bookings = Booking.query.all()
    else:
        bookings = Booking.query.filter_by(customer_id=request.current_user_id).all()
    
    return jsonify([booking.to_dict() for booking in bookings])


@api_bp.route('/bookings', methods=['POST'])
@token_required
def create_booking():
    """Create a new booking."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['car_id', 'pickup_date', 'return_date', 'pickup_location']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check car availability
    car = Car.query.get_or_404(data['car_id'])
    if not car.is_available:
        return jsonify({'error': 'Car is not available'}), 400
    
    # Create booking
    from datetime import datetime
    
    pickup_date = datetime.fromisoformat(data['pickup_date'])
    return_date = datetime.fromisoformat(data['return_date'])
    total_days = (return_date - pickup_date).days
    
    if total_days < 1:
        total_days = 1
    
    subtotal = car.calculate_rental_cost(total_days)
    tax_amount = subtotal * 0.1
    total_amount = subtotal + tax_amount
    
    booking = Booking(
        customer_id=request.current_user_id,
        car_id=car.id,
        pickup_date=pickup_date,
        return_date=return_date,
        pickup_location=data['pickup_location'],
        return_location=data.get('return_location', data['pickup_location']),
        daily_rate=car.daily_rate,
        total_days=total_days,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        customer_notes=data.get('notes')
    )
    
    booking.generate_booking_number()
    
    # Update car status
    from app.models.car import CarStatus
    car.status = CarStatus.BOOKED
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify(booking.to_dict()), 201


@api_bp.route('/bookings/<int:id>', methods=['GET'])
@token_required
def get_booking(id):
    """Get booking by ID."""
    booking = Booking.query.get_or_404(id)
    
    if request.current_user_role not in ['admin', 'manager'] and booking.customer_id != request.current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(booking.to_dict())


@api_bp.route('/bookings/<int:id>/cancel', methods=['POST'])
@token_required
def cancel_booking(id):
    """Cancel a booking."""
    booking = Booking.query.get_or_404(id)
    
    if request.current_user_role not in ['admin', 'manager'] and booking.customer_id != request.current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not booking.can_cancel:
        return jsonify({'error': 'Booking cannot be cancelled'}), 400
    
    from datetime import datetime
    from app.models.booking import BookingStatus
    from app.models.car import CarStatus
    
    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.utcnow()
    booking.cancellation_reason = request.get_json().get('reason', 'Customer requested')
    
    # Update car status
    if booking.car:
        booking.car.status = CarStatus.AVAILABLE
    
    db.session.commit()
    
    return jsonify({'message': 'Booking cancelled successfully', 'booking': booking.to_dict()})


# Payment endpoints
@api_bp.route('/payments', methods=['GET'])
@token_required
def get_payments():
    """Get payments for current user or all payments (admin)."""
    if request.current_user_role in ['admin', 'manager']:
        payments = Payment.query.all()
    else:
        payments = Payment.query.filter_by(user_id=request.current_user_id).all()
    
    return jsonify([payment.to_dict() for payment in payments])


@api_bp.route('/payments/<int:id>', methods=['GET'])
@token_required
def get_payment(id):
    """Get payment by ID."""
    payment = Payment.query.get_or_404(id)
    
    if request.current_user_role not in ['admin', 'manager'] and payment.user_id != request.current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(payment.to_dict())


# Statistics endpoints
@api_bp.route('/stats/dashboard')
@token_required
def dashboard_stats():
    """Get dashboard statistics (admin only)."""
    if request.current_user_role not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    from sqlalchemy import func
    
    stats = {
        'total_users': User.query.count(),
        'total_cars': Car.query.count(),
        'available_cars': Car.query.filter_by(status='available').count(),
        'total_bookings': Booking.query.count(),
        'active_bookings': Booking.query.filter_by(status='in_progress').count(),
        'total_revenue': db.session.query(func.sum(Payment.amount)).filter_by(
            status='completed').scalar() or 0,
        'total_drivers': Driver.query.count(),
        'available_drivers': Driver.query.filter_by(status='available').count()
    }
    
    return jsonify(stats)