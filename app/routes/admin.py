from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc
from app import db
from app.models import User, Car, Booking, Payment, Maintenance, CarStatus, BookingStatus, MaintenanceType, MaintenanceStatus, PaymentStatus
import json
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_manager:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with statistics and charts."""
    # Get statistics
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter(
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])
    ).count()
    total_cars = Car.query.count()
    available_cars = Car.query.filter_by(status=CarStatus.AVAILABLE).count()
    total_users = User.query.count()
    total_revenue = db.session.query(func.sum(Payment.amount)).filter_by(
        status=PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    
    # Get monthly revenue for chart
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_revenue = db.session.query(
        func.strftime('%Y-%m', Payment.created_at).label('month'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        Payment.created_at >= six_months_ago,
        Payment.status == PaymentStatus.COMPLETED
    ).group_by('month').all()
    
    # Get booking status distribution
    booking_status_dist = db.session.query(
        Booking.status,
        func.count(Booking.id).label('count')
    ).group_by(Booking.status).all()
    
    # Get fleet status distribution
    fleet_status_dist = db.session.query(
        Car.status,
        func.count(Car.id).label('count')
    ).group_by(Car.status).all()
    
    # Get maintenance statistics
    cars_healthy = Car.query.filter(
        ~Car.status.in_([CarStatus.MAINTENANCE, CarStatus.OUT_OF_SERVICE])
    ).count()
    
    cars_in_service = Car.query.filter_by(status=CarStatus.MAINTENANCE).count()
    
    # Calculate cars due for service
    cars_due_soon = 0
    cars_overdue = 0
    for car in Car.query.all():
        if car.service_status == 'due_soon':
            cars_due_soon += 1
        elif car.service_status == 'overdue':
            cars_overdue += 1
    
    stats = {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'cars_healthy': cars_healthy,
        'cars_due_soon': cars_due_soon,
        'cars_overdue': cars_overdue,
        'cars_in_service': cars_in_service
    }
    
    # Format data for charts
    chart_data = {
        'monthly_revenue': {
            'labels': [item.month for item in monthly_revenue],
            'data': [float(item.revenue) for item in monthly_revenue]
        },
        'booking_status': {
            'labels': [status.value for status, _ in booking_status_dist],
            'data': [count for _, count in booking_status_dist]
        },
        'fleet_status': {
            'labels': [status.value for status, _ in fleet_status_dist],
            'data': [count for _, count in fleet_status_dist]
        }
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_bookings=recent_bookings,
                         chart_data=chart_data)

@admin_bp.route('/bookings')
@admin_required
def bookings():
    """View and manage all bookings."""
    # Get filter parameters
    user_id = request.args.get('user_id', type=int)
    car_id = request.args.get('car_id', type=int)
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search')
    
    # Build query
    query = Booking.query
    
    if user_id:
        query = query.filter_by(customer_id=user_id)
    if car_id:
        query = query.filter_by(car_id=car_id)
    if status:
        query = query.filter_by(status=BookingStatus(status))
    if date_from:
        query = query.filter(Booking.pickup_date >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(Booking.return_date <= datetime.strptime(date_to, '%Y-%m-%d'))
    if search:
        query = query.filter(
            or_(
                Booking.booking_number.contains(search),
                Booking.customer.has(User.email.contains(search)),
                Booking.customer.has(User.first_name.contains(search)),
                Booking.customer.has(User.last_name.contains(search))
            )
        )
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    bookings = query.order_by(Booking.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get all users and cars for filter dropdowns
    users = User.query.order_by(User.first_name).all()
    cars = Car.query.order_by(Car.make, Car.model).all()
    
    return render_template('admin/bookings.html', 
                         bookings=bookings,
                         users=users,
                         cars=cars,
                         BookingStatus=BookingStatus)

@admin_bp.route('/bookings/<int:booking_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_booking(booking_id):
    """Edit booking details."""
    booking = Booking.query.get_or_404(booking_id)
    
    if request.method == 'POST':
        # Update booking details
        booking.car_id = request.form.get('car_id', type=int)
        booking.pickup_date = datetime.strptime(request.form.get('pickup_date'), '%Y-%m-%dT%H:%M')
        booking.return_date = datetime.strptime(request.form.get('return_date'), '%Y-%m-%dT%H:%M')
        booking.status = BookingStatus(request.form.get('status'))
        booking.pickup_location = request.form.get('pickup_location')
        booking.return_location = request.form.get('return_location')
        booking.admin_notes = request.form.get('admin_notes')
        
        # Handle cancellation
        if booking.status == BookingStatus.CANCELLED:
            booking.cancelled_at = datetime.utcnow()
            booking.cancellation_reason = request.form.get('cancellation_reason')
            # Free up the car
            if booking.car:
                booking.car.status = CarStatus.AVAILABLE
        
        db.session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('admin.bookings'))
    
    cars = Car.query.filter_by(is_active=True).all()
    return render_template('admin/edit_booking.html', booking=booking, cars=cars, BookingStatus=BookingStatus)

@admin_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@admin_required
def cancel_booking(booking_id):
    """Cancel a booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.can_cancel:
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = request.form.get('reason', 'Cancelled by admin')
        
        # Free up the car
        if booking.car:
            booking.car.status = CarStatus.AVAILABLE
        
        db.session.commit()
        flash('Booking cancelled successfully!', 'success')
    else:
        flash('This booking cannot be cancelled.', 'danger')
    
    return redirect(url_for('admin.bookings'))

@admin_bp.route('/fleet')
@admin_required
def fleet():
    """Fleet management page."""
    # Get filter parameters
    status = request.args.get('status')
    category = request.args.get('category')
    search = request.args.get('search')
    
    # Build query
    query = Car.query
    
    if status:
        query = query.filter_by(status=CarStatus(status))
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(
            or_(
                Car.make.contains(search),
                Car.model.contains(search),
                Car.license_plate.contains(search),
                Car.vin.contains(search)
            )
        )
    
    cars = query.order_by(Car.make, Car.model).all()
    
    return render_template('admin/fleet.html', cars=cars, CarStatus=CarStatus)

@admin_bp.route('/fleet/add', methods=['GET', 'POST'])
@admin_required
def add_car():
    """Add a new car to the fleet."""
    if request.method == 'POST':
        car = Car(
            make=request.form.get('make'),
            model=request.form.get('model'),
            year=request.form.get('year', type=int),
            license_plate=request.form.get('license_plate'),
            vin=request.form.get('vin'),
            category=request.form.get('category'),
            seats=request.form.get('seats', type=int),
            transmission=request.form.get('transmission'),
            fuel_type=request.form.get('fuel_type'),
            daily_rate=request.form.get('daily_rate', type=float),
            weekly_rate=request.form.get('weekly_rate', type=float),
            monthly_rate=request.form.get('monthly_rate', type=float),
            color=request.form.get('color'),
            agency=request.form.get('agency'),
            current_odometer=request.form.get('current_odometer', type=int, default=0),
            last_service_odometer=request.form.get('last_service_odometer', type=int, default=0),
            service_threshold=request.form.get('service_threshold', type=int, default=5000),
            status=CarStatus.AVAILABLE
        )
        
        # Handle features as JSON
        features = request.form.getlist('features')
        if features:
            car.features = features
        
        db.session.add(car)
        db.session.flush()  # Flush to get the car ID before committing
        
        # Handle image uploads
        if 'images' in request.files:
            files = request.files.getlist('images')
            uploaded_images = []
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join('static', 'uploads', 'cars')
            os.makedirs(upload_dir, exist_ok=True)
            
            for file in files:
                if file and file.filename:
                    # Secure the filename
                    filename = secure_filename(file.filename)
                    # Add timestamp to make filename unique
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{car.id}_{timestamp}_{filename}"
                    filepath = os.path.join(upload_dir, filename)
                    
                    # Save the file
                    file.save(filepath)
                    
                    # Store the relative path for web access
                    web_path = f"/static/uploads/cars/{filename}"
                    uploaded_images.append(web_path)
            
            if uploaded_images:
                car.images = uploaded_images
        
        db.session.commit()
        
        flash('Car added successfully!', 'success')
        return redirect(url_for('admin.fleet'))
    
    return render_template('admin/add_car.html')

@admin_bp.route('/fleet/<int:car_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_car(car_id):
    """Edit car details."""
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        car.make = request.form.get('make')
        car.model = request.form.get('model')
        car.year = request.form.get('year', type=int)
        car.license_plate = request.form.get('license_plate')
        car.vin = request.form.get('vin')
        car.category = request.form.get('category')
        car.seats = request.form.get('seats', type=int)
        car.transmission = request.form.get('transmission')
        car.fuel_type = request.form.get('fuel_type')
        car.daily_rate = request.form.get('daily_rate', type=float)
        car.weekly_rate = request.form.get('weekly_rate', type=float)
        car.monthly_rate = request.form.get('monthly_rate', type=float)
        car.color = request.form.get('color')
        car.agency = request.form.get('agency')
        car.current_odometer = request.form.get('current_odometer', type=int)
        car.last_service_odometer = request.form.get('last_service_odometer', type=int)
        car.service_threshold = request.form.get('service_threshold', type=int)
        car.status = CarStatus(request.form.get('status'))
        
        # Handle features as JSON
        features = request.form.getlist('features')
        if features:
            car.features = features
        
        db.session.commit()
        flash('Car updated successfully!', 'success')
        return redirect(url_for('admin.fleet'))
    
    return render_template('admin/edit_car.html', car=car, CarStatus=CarStatus)

@admin_bp.route('/fleet/<int:car_id>/delete', methods=['POST'])
@admin_required
def delete_car(car_id):
    """Delete a car from the fleet."""
    car = Car.query.get_or_404(car_id)
    
    # Check if car has active bookings
    active_bookings = Booking.query.filter_by(car_id=car_id).filter(
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])
    ).count()
    
    if active_bookings > 0:
        flash('Cannot delete car with active bookings!', 'danger')
    else:
        db.session.delete(car)
        db.session.commit()
        flash('Car deleted successfully!', 'success')
    
    return redirect(url_for('admin.fleet'))

@admin_bp.route('/fleet/<int:car_id>/images')
@admin_required
def view_car_images(car_id):
    """View car images."""
    car = Car.query.get_or_404(car_id)
    return render_template('admin/view_car_images.html', car=car)

@admin_bp.route('/fleet/<int:car_id>/upload-images', methods=['POST'])
@admin_required
def upload_car_images(car_id):
    """Upload images for a car."""
    car = Car.query.get_or_404(car_id)
    
    if 'images' not in request.files:
        flash('No images selected', 'danger')
        return redirect(url_for('admin.view_car_images', car_id=car_id))
    
    files = request.files.getlist('images')
    uploaded_images = []
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join('static', 'uploads', 'cars')
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        if file and file.filename:
            # Secure the filename
            filename = secure_filename(file.filename)
            # Add timestamp to make filename unique
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{car_id}_{timestamp}_{filename}"
            filepath = os.path.join(upload_dir, filename)
            
            # Save the file
            file.save(filepath)
            
            # Store the relative path for web access
            web_path = f"/static/uploads/cars/{filename}"
            uploaded_images.append(web_path)
    
    # Update car images
    if car.images:
        car.images = car.images + uploaded_images
    else:
        car.images = uploaded_images
    
    db.session.commit()
    flash(f'Successfully uploaded {len(uploaded_images)} image(s)', 'success')
    
    return redirect(url_for('admin.view_car_images', car_id=car_id))

@admin_bp.route('/fleet/<int:car_id>/delete-image', methods=['POST'])
@admin_required
def delete_car_image(car_id):
    """Delete a specific image from a car."""
    car = Car.query.get_or_404(car_id)
    data = request.get_json()
    image_url = data.get('image_url')
    
    if not image_url:
        return jsonify({'success': False, 'message': 'No image URL provided'}), 400
    
    if car.images and image_url in car.images:
        # Remove the image from the list
        car.images = [img for img in car.images if img != image_url]
        
        # Try to delete the physical file
        try:
            # Convert web path to file path
            if image_url.startswith('/static/'):
                file_path = image_url[1:]  # Remove leading slash
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Error deleting file: {e}")
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Image deleted successfully'})
    
    return jsonify({'success': False, 'message': 'Image not found'}), 404

@admin_bp.route('/fleet/<int:car_id>/maintenance', methods=['POST'])
@admin_required
def set_maintenance(car_id):
    """Set a car to maintenance status."""
    car = Car.query.get_or_404(car_id)
    car.status = CarStatus.MAINTENANCE
    
    # Create maintenance record
    maintenance = Maintenance(
        car_id=car_id,
        type=MaintenanceType(request.form.get('type', 'routine')),
        service_date=datetime.strptime(request.form.get('service_date'), '%Y-%m-%d'),
        description=request.form.get('description'),
        status=MaintenanceStatus.SCHEDULED
    )
    
    db.session.add(maintenance)
    db.session.commit()
    
    flash('Car set to maintenance status!', 'success')
    return redirect(url_for('admin.fleet'))

@admin_bp.route('/users')
@admin_required
def users():
    """User management page."""
    # Get filter parameters
    role = request.args.get('role')
    search = request.args.get('search')
    
    # Build query
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    if search:
        query = query.filter(
            or_(
                User.email.contains(search),
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.phone.contains(search)
            )
        )
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add a new user."""
    if request.method == 'POST':
        user = User(
            email=request.form.get('email'),
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            phone=request.form.get('phone'),
            role=request.form.get('role', 'customer')
        )
        user.set_password(request.form.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        flash('User added successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user details."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.phone = request.form.get('phone')
        user.role = request.form.get('role')
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    
    # Don't delete admin users
    if user.role == 'admin':
        flash('Cannot delete admin users!', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/payments')
@admin_required
def payments():
    """View payment history."""
    # Get filter parameters
    user_id = request.args.get('user_id', type=int)
    car_id = request.args.get('car_id', type=int)
    booking_id = request.args.get('booking_id', type=int)
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = Payment.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if car_id:
        # Filter by car through booking relationship
        query = query.join(Booking).filter(Booking.car_id == car_id)
    if booking_id:
        query = query.filter_by(booking_id=booking_id)
    if status:
        query = query.filter_by(status=PaymentStatus(status))
    if date_from:
        query = query.filter(Payment.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(Payment.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    payments = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get total amount
    total_amount = query.filter(Payment.status == PaymentStatus.COMPLETED).with_entities(
        func.sum(Payment.amount)
    ).scalar() or 0
    
    # Get all users and cars for filter dropdowns
    users = User.query.order_by(User.first_name, User.last_name).all()
    cars = Car.query.order_by(Car.make, Car.model).all()
    
    return render_template('admin/payments.html', 
                         payments=payments,
                         total_amount=total_amount,
                         users=users,
                         cars=cars,
                         PaymentStatus=PaymentStatus)

@admin_bp.route('/maintenance')
@admin_required
def maintenance():
    """Maintenance tracking page."""
    # Get service statistics
    cars = Car.query.all()
    
    stats = {
        'healthy': 0,
        'due_soon': 0,
        'overdue': 0,
        'in_service': 0
    }
    
    service_alerts = []
    upcoming_services = []
    
    for car in cars:
        status = car.service_status
        if status == 'healthy':
            stats['healthy'] += 1
        elif status == 'due_soon':
            stats['due_soon'] += 1
            upcoming_services.append({
                'car': car,
                'km_remaining': car.km_until_service
            })
        elif status == 'overdue':
            stats['overdue'] += 1
            service_alerts.append({
                'car': car,
                'km_overdue': abs(car.km_until_service)
            })
        elif status == 'in_service':
            stats['in_service'] += 1
    
    # Sort upcoming services by km remaining
    upcoming_services.sort(key=lambda x: x['km_remaining'])
    
    # Get recent service history
    recent_services = Maintenance.query.filter_by(
        status=MaintenanceStatus.COMPLETED
    ).order_by(Maintenance.completion_date.desc()).limit(10).all()
    
    # Get scheduled maintenance
    scheduled_maintenance = Maintenance.query.filter_by(
        status=MaintenanceStatus.SCHEDULED
    ).order_by(Maintenance.service_date).all()
    
    return render_template('admin/maintenance.html',
                         stats=stats,
                         service_alerts=service_alerts,
                         upcoming_services=upcoming_services,
                         recent_services=recent_services,
                         scheduled_maintenance=scheduled_maintenance,
                         MaintenanceType=MaintenanceType)

@admin_bp.route('/maintenance/schedule', methods=['POST'])
@admin_required
def schedule_maintenance():
    """Schedule maintenance for a car."""
    car_id = request.form.get('car_id', type=int)
    car = Car.query.get_or_404(car_id)
    
    maintenance = Maintenance(
        car_id=car_id,
        type=MaintenanceType(request.form.get('type')),
        service_date=datetime.strptime(request.form.get('service_date'), '%Y-%m-%d'),
        description=request.form.get('description'),
        mileage_at_service=car.current_odometer,
        status=MaintenanceStatus.SCHEDULED,
        total_cost=request.form.get('estimated_cost', type=float, default=0)
    )
    
    # Set car to maintenance status
    car.status = CarStatus.MAINTENANCE
    
    db.session.add(maintenance)
    db.session.commit()
    
    flash('Maintenance scheduled successfully!', 'success')
    return redirect(url_for('admin.maintenance'))

@admin_bp.route('/maintenance/<int:maintenance_id>/complete', methods=['POST'])
@admin_required
def complete_maintenance(maintenance_id):
    """Mark maintenance as completed."""
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    
    maintenance.status = MaintenanceStatus.COMPLETED
    maintenance.completion_date = datetime.utcnow().date()
    maintenance.work_performed = request.form.get('work_performed')
    maintenance.labor_cost = request.form.get('labor_cost', type=float, default=0)
    maintenance.parts_cost = request.form.get('parts_cost', type=float, default=0)
    maintenance.total_cost = maintenance.labor_cost + maintenance.parts_cost
    
    # Update car status and odometer
    car = maintenance.car
    car.status = CarStatus.AVAILABLE
    car.last_service_date = maintenance.completion_date
    car.last_service_odometer = car.current_odometer
    
    db.session.commit()
    
    flash('Maintenance completed successfully!', 'success')
    return redirect(url_for('admin.maintenance'))

# API endpoints for AJAX operations
@admin_bp.route('/api/booking/<int:booking_id>/send-invoice', methods=['POST'])
@admin_required
def send_invoice(booking_id):
    """Send invoice for a booking (placeholder)."""
    booking = Booking.query.get_or_404(booking_id)
    # TODO: Implement invoice sending logic
    return jsonify({'success': True, 'message': 'Invoice sending functionality will be implemented'})

@admin_bp.route('/api/booking/<int:booking_id>/payment-history')
@admin_required
def payment_history(booking_id):
    """Get payment history for a booking (placeholder)."""
    booking = Booking.query.get_or_404(booking_id)
    payments = Payment.query.filter_by(booking_id=booking_id).all()
    # TODO: Implement full payment history logic
    return jsonify({
        'success': True,
        'payments': [p.to_dict() for p in payments] if payments else [],
        'message': 'Payment history functionality will be implemented'
    })

@admin_bp.route('/api/booking/<int:booking_id>/handover', methods=['POST'])
@admin_required
def handover_vehicle(booking_id):
    """Handle vehicle handover (placeholder)."""
    booking = Booking.query.get_or_404(booking_id)
    # TODO: Implement handover logic
    return jsonify({'success': True, 'message': 'Handover functionality will be implemented'})

@admin_bp.route('/api/booking/<int:booking_id>/complete', methods=['POST'])
@admin_required
def complete_booking(booking_id):
    """Complete a booking (placeholder)."""
    booking = Booking.query.get_or_404(booking_id)
    # TODO: Implement completion logic
    return jsonify({'success': True, 'message': 'Booking completion functionality will be implemented'})


@admin_bp.route('/settings')
@admin_required
def settings():
    """Admin settings page."""
    return render_template('admin/settings.html')


@admin_bp.route('/xero-settings')
@admin_required
def xero_settings():
    """Xero integration settings page."""
    callback_url = current_app.config.get('XERO_CALLBACK_URL', '')
    return render_template('admin/xero_settings.html', callback_url=callback_url)