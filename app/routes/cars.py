from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Car, CarCategory, CarStatus, Booking
from app.models.booking import BookingStatus
from app.utils.decorators import manager_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os

bp = Blueprint('cars', __name__, url_prefix='/cars')


@bp.route('/')
def index():
    """List all cars."""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = Car.query.filter_by(is_active=True)
    
    # Apply filters
    if category:
        try:
            # Convert string to enum (case-insensitive)
            category_enum = CarCategory.from_any(category)
            query = query.filter_by(category=category_enum)
        except (ValueError, KeyError):
            # Invalid category value, ignore filter
            pass
    if status:
        try:
            # Convert string to enum
            status_enum = CarStatus(status)
            query = query.filter_by(status=status_enum)
        except (ValueError, KeyError):
            # Invalid status value, ignore filter
            pass
    if search:
        # Case-insensitive search
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Car.make.ilike(search_term),
                Car.model.ilike(search_term),
                Car.license_plate.ilike(search_term)
            )
        )
    
    cars = query.order_by(Car.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)

    # Compute next availability date for booked cars on this page
    car_ids = [car.id for car in cars.items]
    next_available_map = {}
    if car_ids:
        # Treat pending as blocking availability for display purposes
        active_statuses = [BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]
        active_bookings = (
            Booking.query
            .filter(
                Booking.car_id.in_(car_ids),
                Booking.status.in_(active_statuses),
                Booking.return_date >= datetime.utcnow()
            )
            .order_by(Booking.return_date.asc())
            .all()
        )
        for booking in active_bookings:
            # Keep the earliest return_date per car
            if booking.car_id not in next_available_map:
                next_available_map[booking.car_id] = booking.return_date
    
    # Check if user has complete profile (for booking eligibility)
    has_complete_profile = False
    missing_details = []
    if current_user.is_authenticated:
        has_complete_profile = current_user.has_complete_driver_details()
        if not has_complete_profile:
            missing_details = current_user.get_missing_details()
    
    return render_template('pages/cars/index.html', 
                         cars=cars,
                         categories=CarCategory,
                         statuses=CarStatus,
                         has_complete_profile=has_complete_profile,
                         missing_details=missing_details,
                         next_available_map=next_available_map)


@bp.route('/<int:id>')
def view(id):
    """View car details."""
    car = Car.query.get_or_404(id)
    if not car.is_active:
        from flask import abort
        abort(404)
    
    # Get recent bookings for this car
    recent_bookings = Booking.query.filter_by(car_id=car.id).order_by(
        Booking.created_at.desc()).limit(5).all()

    # Compute next availability date for this car (earliest active booking return date)
    next_available_date = None
    # Include pending so we show the earliest expected return
    active_statuses = [BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]
    upcoming = (
        Booking.query
        .filter(
            Booking.car_id == car.id,
            Booking.status.in_(active_statuses),
            Booking.return_date >= datetime.utcnow()
        )
        .order_by(Booking.return_date.asc())
        .first()
    )
    if upcoming:
        next_available_date = upcoming.return_date
    
    # Check if user has complete profile (for booking eligibility)
    has_complete_profile = False
    missing_details = []
    if current_user.is_authenticated:
        has_complete_profile = current_user.has_complete_driver_details()
        if not has_complete_profile:
            missing_details = current_user.get_missing_details()
    
    return render_template('pages/cars/view.html', 
                         car=car,
                         recent_bookings=recent_bookings,
                         has_complete_profile=has_complete_profile,
                         missing_details=missing_details,
                         next_available_date=next_available_date)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@manager_required
def create():
    """Add a new car to the fleet."""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Create new car
        # Parse category accepting both enum name and value (case-insensitive)
        category_value = data['category']
        parsed_category = CarCategory.from_any(category_value)

        car = Car(
            make=data['make'],
            model=data['model'],
            year=int(data['year']),
            license_plate=data['license_plate'],
            vin=data['vin'],
            category=parsed_category,
            seats=int(data['seats']),
            transmission=data.get('transmission', 'Automatic'),
            fuel_type=data.get('fuel_type', 'Gasoline'),
            daily_rate=float(data['daily_rate']),
            weekly_rate=float(data.get('weekly_rate', 0)) or None,
            monthly_rate=float(data.get('monthly_rate', 0)) or None,
            color=data.get('color'),
            mileage=int(data.get('mileage', 0)),
            current_location=data.get('current_location', 'Main Office'),
            home_location=data.get('home_location', 'Main Office')
        )
        
        # Handle features
        features = request.form.getlist('features')
        if features:
            car.features = features
        
        # Handle image upload
        if 'main_image' in request.files:
            file = request.files['main_image']
            if file and file.filename:
                from app.services.storage import get_storage
                storage = get_storage()
                filename = secure_filename(file.filename)
                key = storage.generate_key('cars', filename)
                car.main_image = storage.upload_fileobj(file, key, content_type=file.mimetype)
        
        db.session.add(car)
        db.session.commit()
        
        flash(f'Car {car.full_name} added successfully!', 'success')
        return redirect(url_for('cars.view', id=car.id))
    
    return render_template('pages/cars/create.html',
                         categories=CarCategory)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit(id):
    """Edit car details."""
    car = Car.query.get_or_404(id)
    if not car.is_active:
        return jsonify({'error': 'Car not found'}), 404
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Update car fields
        car.make = data.get('make', car.make)
        car.model = data.get('model', car.model)
        car.year = int(data.get('year', car.year))
        car.license_plate = data.get('license_plate', car.license_plate)
        car.vin = data.get('vin', car.vin)
        car.seats = int(data.get('seats', car.seats))
        car.transmission = data.get('transmission', car.transmission)
        car.fuel_type = data.get('fuel_type', car.fuel_type)
        car.daily_rate = float(data.get('daily_rate', car.daily_rate))
        car.weekly_rate = float(data.get('weekly_rate', 0)) or car.weekly_rate
        car.monthly_rate = float(data.get('monthly_rate', 0)) or car.monthly_rate
        car.color = data.get('color', car.color)
        car.mileage = int(data.get('mileage', car.mileage))
        car.current_location = data.get('current_location', car.current_location)
        
        # Update status if changed
        if data.get('status'):
            car.status = CarStatus[data['status'].upper()]
        
        # Update features
        features = request.form.getlist('features')
        if features:
            car.features = features
        
        # Handle new image upload
        if 'main_image' in request.files:
            file = request.files['main_image']
            if file and file.filename:
                from app.services.storage import get_storage
                storage = get_storage()
                filename = secure_filename(file.filename)
                key = storage.generate_key('cars', filename)
                car.main_image = storage.upload_fileobj(file, key, content_type=file.mimetype)
        
        db.session.commit()
        flash('Car updated successfully!', 'success')
        return redirect(url_for('cars.view', id=id))
    
    return render_template('pages/cars/edit.html',
                         car=car,
                         categories=CarCategory,
                         statuses=CarStatus)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@manager_required
def delete(id):
    """Delete a car (soft delete)."""
    car = Car.query.get_or_404(id)
    
    # Check if car has active bookings
    active_bookings = Booking.query.filter_by(car_id=car.id).filter(
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])
    ).count()
    
    if active_bookings > 0:
        flash('Cannot delete car with active bookings.', 'error')
        return redirect(url_for('cars.view', id=id))
    
    # Soft delete
    car.is_active = False
    car.status = CarStatus.OUT_OF_SERVICE
    db.session.commit()
    
    flash('Car removed from fleet.', 'info')
    return redirect(url_for('cars.index'))


@bp.route('/<int:id>/availability')
@login_required
def check_availability(id):
    """Check car availability for specific dates."""
    car = Car.query.get_or_404(id)
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start and end dates required'}), 400
    
    # Check for overlapping bookings
    overlapping = Booking.query.filter(
        Booking.car_id == car.id,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
        db.or_(
            db.and_(
                Booking.pickup_date <= start_date,
                Booking.return_date >= start_date
            ),
            db.and_(
                Booking.pickup_date <= end_date,
                Booking.return_date >= end_date
            ),
            db.and_(
                Booking.pickup_date >= start_date,
                Booking.return_date <= end_date
            )
        )
    ).count()
    
    available = overlapping == 0 and car.is_available
    
    return jsonify({
        'available': available,
        'car_id': car.id,
        'car_name': car.full_name
    })