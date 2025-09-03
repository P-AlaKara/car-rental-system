from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Driver, User, Role, DriverStatus, Booking
from app.utils.decorators import manager_required
from datetime import datetime

bp = Blueprint('drivers', __name__, url_prefix='/drivers')


@bp.route('/')
@login_required
@manager_required
def index():
    """List all drivers."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = Driver.query.join(User)
    
    # Apply filters
    if status:
        query = query.filter(Driver.status == DriverStatus[status.upper()])
    if search:
        query = query.filter(
            db.or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                Driver.employee_id.contains(search),
                Driver.license_number.contains(search)
            )
        )
    
    drivers = query.order_by(Driver.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('pages/drivers/index.html',
                         drivers=drivers,
                         statuses=DriverStatus)


@bp.route('/<int:id>')
@login_required
@manager_required
def view(id):
    """View driver details."""
    driver = Driver.query.get_or_404(id)
    
    # Get driver statistics
    stats = {
        'total_trips': driver.total_trips,
        'total_hours': driver.total_hours,
        'rating': driver.rating,
        'active_bookings': Booking.query.filter_by(
            driver_id=driver.id, status='in_progress').count(),
        'completed_bookings': Booking.query.filter_by(
            driver_id=driver.id, status='completed').count()
    }
    
    # Get recent bookings
    recent_bookings = Booking.query.filter_by(driver_id=driver.id).order_by(
        Booking.created_at.desc()).limit(5).all()
    
    return render_template('pages/drivers/view.html',
                         driver=driver,
                         stats=stats,
                         recent_bookings=recent_bookings)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@manager_required
def create():
    """Register a new driver."""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # First create the user account
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            role=Role.CUSTOMER,  # Drivers are now customers with driver privileges
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create driver profile
        driver = Driver(
            user_id=user.id,
            license_number=data['license_number'],
            license_class=data['license_class'],
            license_expiry=datetime.strptime(data['license_expiry'], '%Y-%m-%d').date(),
            license_state=data.get('license_state'),
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date(),
            hourly_rate=float(data.get('hourly_rate', 0)),
            commission_rate=float(data.get('commission_rate', 0)),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            emergency_contact_relationship=data.get('emergency_contact_relationship'),
            max_daily_hours=int(data.get('max_daily_hours', 8))
        )
        
        # Generate employee ID
        driver.generate_employee_id()
        
        # Set medical and background check dates if provided
        if data.get('medical_cert_expiry'):
            driver.medical_cert_expiry = datetime.strptime(
                data['medical_cert_expiry'], '%Y-%m-%d').date()
        if data.get('background_check_date'):
            driver.background_check_date = datetime.strptime(
                data['background_check_date'], '%Y-%m-%d').date()
        
        db.session.add(driver)
        db.session.commit()
        
        flash(f'Driver {driver.employee_id} registered successfully!', 'success')
        return redirect(url_for('drivers.view', id=driver.id))
    
    return render_template('pages/drivers/create.html')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit(id):
    """Edit driver details."""
    driver = Driver.query.get_or_404(id)
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Update user information
        driver.user.first_name = data['first_name']
        driver.user.last_name = data['last_name']
        driver.user.phone = data['phone']
        driver.user.address = data.get('address')
        driver.user.city = data.get('city')
        driver.user.state = data.get('state')
        driver.user.zip_code = data.get('zip_code')
        
        # Update driver information
        driver.license_number = data['license_number']
        driver.license_class = data['license_class']
        driver.license_expiry = datetime.strptime(data['license_expiry'], '%Y-%m-%d').date()
        driver.license_state = data.get('license_state')
        driver.hourly_rate = float(data.get('hourly_rate', driver.hourly_rate))
        driver.commission_rate = float(data.get('commission_rate', driver.commission_rate))
        driver.emergency_contact_name = data.get('emergency_contact_name')
        driver.emergency_contact_phone = data.get('emergency_contact_phone')
        driver.emergency_contact_relationship = data.get('emergency_contact_relationship')
        driver.max_daily_hours = int(data.get('max_daily_hours', driver.max_daily_hours))
        
        # Update status if changed
        if data.get('status'):
            driver.status = DriverStatus[data['status'].upper()]
        
        # Update dates if provided
        if data.get('medical_cert_expiry'):
            driver.medical_cert_expiry = datetime.strptime(
                data['medical_cert_expiry'], '%Y-%m-%d').date()
        if data.get('background_check_date'):
            driver.background_check_date = datetime.strptime(
                data['background_check_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        flash('Driver updated successfully!', 'success')
        return redirect(url_for('drivers.view', id=id))
    
    return render_template('pages/drivers/edit.html',
                         driver=driver,
                         statuses=DriverStatus)


@bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
@manager_required
def toggle_status(id):
    """Toggle driver active status."""
    driver = Driver.query.get_or_404(id)
    
    driver.is_active = not driver.is_active
    if not driver.is_active:
        driver.status = DriverStatus.OFF_DUTY
    else:
        driver.status = DriverStatus.AVAILABLE
    
    db.session.commit()
    
    status = 'activated' if driver.is_active else 'deactivated'
    flash(f'Driver {status} successfully!', 'success')
    return redirect(url_for('drivers.view', id=id))


@bp.route('/<int:id>/assign', methods=['POST'])
@login_required
@manager_required
def assign_booking(id):
    """Assign a driver to a booking."""
    driver = Driver.query.get_or_404(id)
    booking_id = request.form.get('booking_id')
    
    if not booking_id:
        flash('No booking selected.', 'error')
        return redirect(url_for('drivers.view', id=id))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if driver is available
    if not driver.is_available:
        flash('Driver is not available.', 'error')
        return redirect(url_for('drivers.view', id=id))
    
    # Assign driver to booking
    booking.driver_id = driver.id
    booking.with_driver = True
    
    # Update driver status
    driver.status = DriverStatus.ON_DUTY
    
    db.session.commit()
    flash(f'Driver assigned to booking {booking.booking_number}!', 'success')
    return redirect(url_for('bookings.view', id=booking.id))