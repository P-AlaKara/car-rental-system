from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc
from app import db
from app.models import User, Role, Car, Booking, Payment, Maintenance, CarStatus, BookingStatus, MaintenanceType, MaintenanceStatus, PaymentStatus, VehicleReturn
import json
import os
from werkzeug.utils import secure_filename
import uuid

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
    try:
        # Get statistics with error handling
        try:
            total_bookings = Booking.query.count()
            active_bookings = Booking.query.filter(
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])
            ).count()
        except Exception as e:
            current_app.logger.error(f"Error getting booking stats: {str(e)}")
            total_bookings = 0
            active_bookings = 0
        
        try:
            total_cars = Car.query.count()
            available_cars = Car.query.filter_by(status=CarStatus.AVAILABLE).count()
        except Exception as e:
            current_app.logger.error(f"Error getting car stats: {str(e)}")
            total_cars = 0
            available_cars = 0
        
        try:
            total_users = User.query.count()
        except Exception as e:
            current_app.logger.error(f"Error getting user count: {str(e)}")
            total_users = 0
        
        try:
            total_revenue = db.session.query(func.sum(Payment.amount)).filter_by(
                status=PaymentStatus.COMPLETED
            ).scalar() or 0
        except Exception as e:
            current_app.logger.error(f"Error getting revenue: {str(e)}")
            total_revenue = 0
        
        # Get recent bookings
        try:
            recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
        except Exception as e:
            current_app.logger.error(f"Error getting recent bookings: {str(e)}")
            recent_bookings = []
        
        # Get monthly revenue for chart
        try:
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            monthly_revenue = db.session.query(
                func.strftime('%Y-%m', Payment.created_at).label('month'),
                func.sum(Payment.amount).label('revenue')
            ).filter(
                Payment.created_at >= six_months_ago,
                Payment.status == PaymentStatus.COMPLETED
            ).group_by('month').all()
        except Exception as e:
            current_app.logger.error(f"Error getting monthly revenue: {str(e)}")
            monthly_revenue = []
        
        # Get booking status distribution
        try:
            booking_status_dist = db.session.query(
                Booking.status,
                func.count(Booking.id).label('count')
            ).group_by(Booking.status).all()
        except Exception as e:
            current_app.logger.error(f"Error getting booking distribution: {str(e)}")
            booking_status_dist = []
        
        # Get fleet status distribution
        try:
            fleet_status_dist = db.session.query(
                Car.status,
                func.count(Car.id).label('count')
            ).group_by(Car.status).all()
        except Exception as e:
            current_app.logger.error(f"Error getting fleet distribution: {str(e)}")
            fleet_status_dist = []
        
        # Get maintenance statistics
        cars_healthy = 0
        cars_in_service = 0
        cars_due_soon = 0
        cars_overdue = 0
        
        try:
            cars_healthy = Car.query.filter(
                ~Car.status.in_([CarStatus.MAINTENANCE, CarStatus.OUT_OF_SERVICE])
            ).count()
            
            cars_in_service = Car.query.filter_by(status=CarStatus.MAINTENANCE).count()
            
            # Calculate cars due for service
            for car in Car.query.all():
                if hasattr(car, 'service_status'):
                    if car.service_status == 'due_soon':
                        cars_due_soon += 1
                    elif car.service_status == 'overdue':
                        cars_overdue += 1
        except Exception as e:
            current_app.logger.error(f"Error getting maintenance stats: {str(e)}")
        
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
                'labels': [item.month for item in monthly_revenue] if monthly_revenue else [],
                'data': [float(item.revenue) for item in monthly_revenue] if monthly_revenue else []
            },
            'booking_status': {
                'labels': [status.value for status, _ in booking_status_dist] if booking_status_dist else [],
                'data': [count for _, count in booking_status_dist] if booking_status_dist else []
            },
            'fleet_status': {
                'labels': [status.value for status, _ in fleet_status_dist] if fleet_status_dist else [],
                'data': [count for _, count in fleet_status_dist] if fleet_status_dist else []
            }
        }
        
        return render_template('admin/dashboard.html', 
                             stats=stats, 
                             recent_bookings=recent_bookings,
                             chart_data=chart_data)
    except Exception as e:
        current_app.logger.error(f"Critical error in admin dashboard: {str(e)}")
        # Return with all default values
        return render_template('admin/dashboard.html', 
                             stats={
                                 'total_bookings': 0,
                                 'active_bookings': 0,
                                 'total_cars': 0,
                                 'available_cars': 0,
                                 'total_users': 0,
                                 'total_revenue': 0,
                                 'cars_healthy': 0,
                                 'cars_due_soon': 0,
                                 'cars_overdue': 0,
                                 'cars_in_service': 0
                             }, 
                             recent_bookings=[],
                             chart_data={
                                 'monthly_revenue': {'labels': [], 'data': []},
                                 'booking_status': {'labels': [], 'data': []},
                                 'fleet_status': {'labels': [], 'data': []}
                             })

@admin_bp.route('/bookings')
@admin_required
def bookings():
    """View and manage all bookings."""
    try:
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
            try:
                query = query.filter_by(status=BookingStatus(status))
            except ValueError:
                current_app.logger.warning(f"Invalid booking status: {status}")
                # Ignore invalid status
        if date_from:
            try:
                query = query.filter(Booking.pickup_date >= datetime.strptime(date_from, '%Y-%m-%d'))
            except ValueError:
                current_app.logger.warning(f"Invalid date_from format: {date_from}")
        if date_to:
            try:
                query = query.filter(Booking.return_date <= datetime.strptime(date_to, '%Y-%m-%d'))
            except ValueError:
                current_app.logger.warning(f"Invalid date_to format: {date_to}")
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
    except Exception as e:
        current_app.logger.error(f"Error loading bookings: {str(e)}")
        flash('An error occurred while loading bookings. Please try again.', 'danger')
        # Return empty results on error - create a simple mock pagination object
        class EmptyPagination:
            def __init__(self):
                self.items = []
                self.total = 0
                self.page = 1
                self.pages = 0
                self.per_page = 20
                self.has_prev = False
                self.has_next = False
                self.prev_num = None
                self.next_num = None
            def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
                return []
        
        empty_bookings = EmptyPagination()
        return render_template('admin/bookings.html', 
                             bookings=empty_bookings,
                             users=[],
                             cars=[],
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
    try:
        # Get filter parameters
        role = request.args.get('role')
        search = request.args.get('search')
        
        # Build query
        query = User.query
        
        if role:
            # Convert string role to Role enum
            try:
                role_enum = Role[role.upper()]
                query = query.filter_by(role=role_enum)
            except (KeyError, AttributeError):
                # Invalid role, skip filter
                pass
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
    except Exception as e:
        current_app.logger.error(f"Error loading users: {str(e)}")
        flash('An error occurred while loading users. Please try again.', 'danger')
        # Return empty results on error - create a simple mock pagination object
        class EmptyPagination:
            def __init__(self):
                self.items = []
                self.total = 0
                self.page = 1
                self.pages = 0
                self.per_page = 20
                self.has_prev = False
                self.has_next = False
                self.prev_num = None
                self.next_num = None
            def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
                return []
        
        empty_users = EmptyPagination()
        return render_template('admin/users.html', users=empty_users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add a new user."""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('User with this email already exists!', 'danger')
                return redirect(url_for('admin.add_user'))
            
            # Generate username from email (part before @) or from first_last name
            username = request.form.get('username')
            if not username:
                # Try to generate from email
                if email and '@' in email:
                    username = email.split('@')[0]
                else:
                    # Generate from name
                    username = f"{first_name.lower()}.{last_name.lower()}" if first_name and last_name else None
            
            # Ensure username is unique
            if username:
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
            
            # Get role from form and convert to enum
            role_value = request.form.get('role', 'customer')
            
            # Map HTML form values to Role enum values
            role_mapping = {
                'customer': Role.CUSTOMER,
                'staff': Role.ADMIN,  # Map legacy staff/driver/manager to ADMIN
                'driver': Role.ADMIN,  # Map legacy driver to ADMIN
                'manager': Role.ADMIN,  # Map legacy manager to ADMIN
                'admin': Role.ADMIN
            }
            
            # Get the role enum value, default to CUSTOMER if not found
            user_role = role_mapping.get(role_value.lower(), Role.CUSTOMER)
            
            user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone=request.form.get('phone'),
                role=user_role
            )
            user.set_password(request.form.get('password'))
            
            db.session.add(user)
            db.session.commit()
            
            flash('User added successfully!', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding user: {str(e)}")
            flash(f'Error adding user: {str(e)}', 'danger')
            return redirect(url_for('admin.add_user'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user details."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            user.email = request.form.get('email')
            user.first_name = request.form.get('first_name')
            user.last_name = request.form.get('last_name')
            user.phone = request.form.get('phone')
            
            # Get role from form and convert to enum
            role_value = request.form.get('role', 'customer')
            
            # Map HTML form values to Role enum values
            role_mapping = {
                'customer': Role.CUSTOMER,
                'staff': Role.ADMIN,  # Map legacy staff/driver/manager to ADMIN
                'driver': Role.ADMIN,  # Map legacy driver to ADMIN
                'manager': Role.ADMIN,  # Map legacy manager to ADMIN
                'admin': Role.ADMIN
            }
            
            # Get the role enum value, keep existing if not found
            user.role = role_mapping.get(role_value.lower(), user.role)
            
            # Update password if provided
            new_password = request.form.get('password')
            if new_password:
                user.set_password(new_password)
            
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user: {str(e)}")
            flash(f'Error updating user: {str(e)}', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    
    # Don't delete admin users
    if user.role == Role.ADMIN:
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
    try:
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
            try:
                query = query.filter_by(status=PaymentStatus(status))
            except ValueError:
                current_app.logger.warning(f"Invalid payment status: {status}")
                # Ignore invalid status
        if date_from:
            try:
                query = query.filter(Payment.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
            except ValueError:
                current_app.logger.warning(f"Invalid date_from format: {date_from}")
        if date_to:
            try:
                query = query.filter(Payment.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
            except ValueError:
                current_app.logger.warning(f"Invalid date_to format: {date_to}")
        
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
    except Exception as e:
        current_app.logger.error(f"Error loading payments: {str(e)}")
        flash('An error occurred while loading payments. Please try again.', 'danger')
        # Return empty results on error - create a simple mock pagination object
        class EmptyPagination:
            def __init__(self):
                self.items = []
                self.total = 0
                self.page = 1
                self.pages = 0
                self.per_page = 20
                self.has_prev = False
                self.has_next = False
                self.prev_num = None
                self.next_num = None
            def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
                return []
        
        empty_payments = EmptyPagination()
        return render_template('admin/payments.html', 
                             payments=empty_payments,
                             total_amount=0,
                             users=[],
                             cars=[],
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

@admin_bp.route('/booking/<int:booking_id>/send-invoice')
@admin_required
def show_send_invoice(booking_id):
    """Show the send invoice page for a booking."""
    from app.models import XeroToken
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if Xero is connected
    xero_token = XeroToken.query.order_by(XeroToken.created_at.desc()).first()
    xero_connected = xero_token is not None and xero_token.refresh_token is not None
    
    return render_template('admin/send_invoice.html', 
                         booking=booking, 
                         xero_connected=xero_connected,
                         xero_auth_url=url_for('xero.authorize', _external=True))

# API endpoints for AJAX operations
@admin_bp.route('/api/booking/<int:booking_id>/send-invoice', methods=['POST'])
@admin_required
def send_invoice(booking_id):
    """Send invoice for a booking through Xero."""
    from app.models import XeroToken
    from app.utils.xero import XeroClient
    import logging
    
    logger = logging.getLogger(__name__)
    booking = Booking.query.get_or_404(booking_id)
    
    try:
        # Get custom invoice amount and due date from request (be tolerant of empty body)
        data = request.get_json(silent=True) or {}
        custom_invoice_amount = data.get('invoice_amount')
        custom_due_date = data.get('due_date')
        # Check if we have a Xero token (refresh token)
        xero_token = XeroToken.query.order_by(XeroToken.created_at.desc()).first()
        
        if not xero_token or not xero_token.refresh_token:
            # No token available - first time connection or token deleted
            return jsonify({
                'success': False,
                'needs_auth': True,
                'auth_url': url_for('xero.authorize', _external=True),
                'message': 'Xero connection required. Please authorize the application first.'
            }), 401
        
        # Get customer details
        customer = User.query.get(booking.customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found for this booking'
            }), 404
        
        # Prepare booking data for invoice
        booking_data = {
            'booking_number': booking.booking_number,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'customer_email': customer.email,
            'customer_phone': customer.phone or '',
            'car_name': booking.car.full_name if booking.car else 'N/A',
            'pickup_date': booking.pickup_date.strftime('%Y-%m-%d') if booking.pickup_date else None,
            'return_date': booking.return_date.strftime('%Y-%m-%d') if booking.return_date else None,
            'pickup_location': booking.pickup_location,
            'return_location': booking.return_location,
            'daily_rate': booking.daily_rate,
            'total_days': booking.total_days,
            'with_driver': booking.with_driver,
            'insurance_opted': booking.insurance_opted,
            'gps_opted': booking.gps_opted,
            'child_seat_opted': booking.child_seat_opted
        }
        
        # Use custom due date or calculate default (7 days from now)
        from datetime import datetime, timedelta
        if custom_due_date:
            try:
                due_date = datetime.strptime(custom_due_date, '%Y-%m-%d')
            except:
                due_date = datetime.utcnow() + timedelta(days=7)
        else:
            due_date = datetime.utcnow() + timedelta(days=7)
        
        # Initialize Xero client and send invoice
        client = XeroClient()
        
        try:
            # Use custom invoice amount if provided, otherwise use booking total
            invoice_amount = float(custom_invoice_amount) if custom_invoice_amount else float(booking.total_amount)
            
            # This will automatically refresh the token if needed
            result = client.create_and_send_invoice(
                booking_data=booking_data,
                invoice_amount=invoice_amount,
                due_date=due_date
            )
            
            # Store invoice reference in booking
            if result.get('invoice'):
                invoice_info = result['invoice']
                booking.admin_notes = (booking.admin_notes or '') + f"\nXero Invoice: {invoice_info.get('InvoiceNumber')} (ID: {invoice_info.get('InvoiceID')})"
                db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Invoice sent successfully',
                'invoice_number': result.get('invoice', {}).get('InvoiceNumber'),
                'invoice_id': result.get('invoice', {}).get('InvoiceID')
            })
            
        except Exception as xero_error:
            # Check if the error is due to invalid/expired refresh token
            error_msg = str(xero_error).lower()
            if 'invalid_grant' in error_msg or 'refresh' in error_msg or 'expired' in error_msg:
                # Token is invalid - need to re-authorize
                return jsonify({
                    'success': False,
                    'needs_auth': True,
                    'auth_url': url_for('xero.authorize', _external=True),
                    'message': 'Xero authorization expired. Please re-authorize the application.'
                }), 401
            else:
                # Other Xero error
                logger.error(f"Xero error sending invoice: {str(xero_error)}")
                return jsonify({
                    'success': False,
                    'message': f'Failed to send invoice: {str(xero_error)}'
                }), 500
                
    except Exception as e:
        logger.error(f"Error processing invoice request: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        }), 500

@admin_bp.route('/api/booking/<int:booking_id>/payment-history')
@admin_required
def payment_history(booking_id):
    """Get payment schedule and payments for a booking."""
    try:
        booking = Booking.query.get_or_404(booking_id)
        # Fetch installments from direct debit schedule if present
        installments = []
        from app.models import DirectDebitInstallment, DirectDebitSchedule
        dds = None
        if booking.direct_debit_schedule_id:
            dds = DirectDebitSchedule.query.filter_by(schedule_id=booking.direct_debit_schedule_id).first()
            if dds:
                installments = DirectDebitInstallment.query.filter_by(booking_id=booking.id).order_by(DirectDebitInstallment.due_date.asc()).all()

        # Also include any Payment records tied to the booking
        payments = Payment.query.filter_by(booking_id=booking_id).order_by(Payment.created_at.desc()).all()

        # Build table rows with status logic: pending (future, unpaid), completed (paid), overdue (past due, unpaid)
        rows = []
        from datetime import date
        today = date.today()
        for inst in installments:
            status = inst.status
            if inst.paid_date and (inst.paid_amount or 0) > 0:
                status = 'completed'
            elif inst.due_date and inst.due_date < today:
                # Only overdue if not completed
                status = 'overdue' if status != 'completed' else 'completed'
            else:
                status = 'pending' if status not in ['completed', 'overdue'] else status

            rows.append({
                'due_date': inst.due_date.isoformat() if inst.due_date else None,
                'due_amount': inst.due_amount,
                'paid_date': inst.paid_date.isoformat() if inst.paid_date else None,
                'paid_amount': inst.paid_amount,
                'status': status
            })

        return jsonify({
            'success': True,
            'schedule': {
                'exists': bool(dds),
                'schedule_id': dds.schedule_id if dds else None,
                'description': dds.description if dds else None
            },
            'rows': rows,
            'payments': [p.to_dict() for p in payments],
            'message': 'No scheduled payments found' if not rows else ''
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching payment history: {e}")
        return jsonify({'success': False, 'message': 'Failed to load payment history'}), 500

@admin_bp.route('/api/booking/<int:booking_id>/handover-details', methods=['GET'])
@admin_required
def get_handover_details(booking_id):
    """Get booking details for handover process."""
    booking = Booking.query.get_or_404(booking_id)
    customer = booking.customer
    
    return jsonify({
        'booking': {
            'id': booking.id,
            'booking_number': booking.booking_number,
            'total_amount': booking.total_amount,
            'deposit_amount': booking.deposit_amount,
            'daily_rate': booking.daily_rate,
            'pickup_date': booking.pickup_date.isoformat() if booking.pickup_date else None,
            'return_date': booking.return_date.isoformat() if booking.return_date else None
        },
        'customer': {
            'id': customer.id,
            'full_name': customer.full_name,
            'email': customer.email,
            'phone': customer.phone,
            'license_number': customer.license_number,
            'license_expiry': customer.license_expiry.isoformat() if customer.license_expiry else None,
            'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None
        },
        'car': {
            'id': booking.car.id,
            'name': booking.car.full_name,
            'license_plate': booking.car.license_plate
        }
    })

@admin_bp.route('/api/booking/<int:booking_id>/complete-handover', methods=['POST'])
@admin_required
def complete_handover(booking_id):
    """Complete the vehicle handover process."""
    from app.services.pay_advantage import PayAdvantageService
    from app.models import BookingPhoto, DirectDebitSchedule
    import base64
    from io import BytesIO
    from PIL import Image
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != BookingStatus.CONFIRMED:
        return jsonify({'success': False, 'message': 'Booking must be confirmed to process handover'})
    
    data = request.get_json()
    
    try:
        # 1. Update license verification
        if data.get('license_verified'):
            booking.license_verified = True
            booking.license_verified_at = datetime.utcnow()
        
        # 2. Store odometer reading
        if data.get('odometer_reading'):
            booking.pickup_odometer = data['odometer_reading']
        
        # 3. Save photos
        photos = data.get('photos', [])
        for photo_data in photos:
            # Process base64 image data
            if 'data' in photo_data and photo_data['data'].startswith('data:image'):
                # Extract base64 data
                header, encoded = photo_data['data'].split(',', 1)
                
                # Save to file system (you might want to use cloud storage in production)
                filename = f"pickup_{booking_id}_{uuid.uuid4().hex[:8]}.jpg"
                filepath = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'booking_photos', filename)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Decode and save image
                image_data = base64.b64decode(encoded)
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Save photo record to database
                photo = BookingPhoto(
                    booking_id=booking_id,
                    photo_type='pickup',
                    photo_url=f'/uploads/booking_photos/{filename}',
                    description=photo_data.get('name', ''),
                    uploaded_by=current_user.id
                )
                db.session.add(photo)
        
        # 4. Set up direct debit if provided
        direct_debit = data.get('direct_debit')
        authorization_url = None
        
        if direct_debit and (direct_debit.get('upfront_amount') or direct_debit.get('recurring_amount')):
            try:
                # Initialize PayAdvantage service
                pa_service = PayAdvantageService()
                
                # Get or create customer
                pa_customer = pa_service.get_or_create_customer(booking.customer)
                
                # Create direct debit schedule
                
                upfront_date = None
                if direct_debit.get('upfront_date'):
                    upfront_date = datetime.strptime(direct_debit['upfront_date'], '%Y-%m-%d').date()
                
                recurring_start = None
                if direct_debit.get('recurring_start_date'):
                    recurring_start = datetime.strptime(direct_debit['recurring_start_date'], '%Y-%m-%d').date()
                
                result = pa_service.create_direct_debit_schedule(
                    booking_id=booking_id,
                    customer_code=pa_customer.customer_code,
                    description=direct_debit.get('description', f'Booking {booking.booking_number}'),
                    upfront_amount=direct_debit.get('upfront_amount'),
                    upfront_date=upfront_date,
                    recurring_amount=direct_debit.get('recurring_amount'),
                    recurring_start_date=recurring_start,
                    frequency=direct_debit.get('frequency'),
                    end_condition_amount=direct_debit.get('end_condition_amount'),
                    reminder_days=2
                )
                
                booking.direct_debit_schedule_id = result['schedule_id']
                authorization_url = result['authorization_url']
                
            except Exception as e:
                print(f"Error setting up direct debit: {e}")
                # Continue with handover even if direct debit fails
        
        # 5. Update booking status and handover completion
        booking.status = BookingStatus.IN_PROGRESS
        booking.handover_completed_at = datetime.utcnow()
        booking.handover_completed_by = current_user.id
        booking.actual_pickup_date = datetime.utcnow()
        
        # Add admin note
        handover_note = f"Handover completed by {current_user.full_name} at {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        if booking.admin_notes:
            booking.admin_notes += f"\n{handover_note}"
        else:
            booking.admin_notes = handover_note
        
        db.session.commit()
        
        # 6. Schedule Xero invoice if direct debit is set up
        if direct_debit and direct_debit.get('recurring_amount'):
            from app.services.xero_scheduler import XeroInvoiceScheduler
            scheduler = XeroInvoiceScheduler()
            scheduler.schedule_recurring_invoices(booking_id)
        
        response = {
            'success': True,
            'message': 'Handover completed successfully'
        }
        
        if authorization_url:
            response['authorization_url'] = authorization_url
            response['message'] += '. Direct debit authorization required.'
        
        return jsonify(response)
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in handover: {e}")
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/api/booking/<int:booking_id>/return-details', methods=['GET'])
@admin_required
def get_return_details(booking_id):
    """Get booking details for return process."""
    booking = Booking.query.get_or_404(booking_id)
    customer = booking.customer
    car = booking.car
    
    return jsonify({
        'booking': {
            'id': booking.id,
            'booking_number': booking.booking_number,
            'pickup_date': booking.pickup_date.strftime('%Y-%m-%d') if booking.pickup_date else '',
            'return_date': booking.return_date.strftime('%Y-%m-%d') if booking.return_date else '',
            'total_amount': booking.total_amount,
            'deposit_amount': booking.deposit_amount
        },
        'customer': {
            'id': customer.id if customer else None,
            'full_name': customer.full_name if customer else 'N/A',
            'email': customer.email if customer else 'N/A',
            'phone': customer.phone if customer else 'N/A'
        },
        'car': {
            'id': car.id if car else None,
            'full_name': car.full_name if car else 'N/A',
            'license_plate': car.license_plate if car else 'N/A'
        }
    })

@admin_bp.route('/api/booking/<int:booking_id>/process-return', methods=['POST'])
@admin_required
def process_return(booking_id):
    """Process vehicle return."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if booking is in progress
    if booking.status != BookingStatus.IN_PROGRESS:
        return jsonify({'success': False, 'message': 'Only in-progress bookings can be returned'})
    
    # Check if return already exists
    existing_return = VehicleReturn.query.filter_by(booking_id=booking_id).first()
    if existing_return:
        return jsonify({'success': False, 'message': 'Return has already been processed for this booking'})
    
    try:
        data = request.get_json()
        
        # Create vehicle return record
        vehicle_return = VehicleReturn(
            booking_id=booking_id,
            bond_returned=data.get('bond_returned', False),
            all_payments_received=data.get('all_payments_received', False),
            car_in_good_condition=data.get('car_in_good_condition', False),
            fuel_tank_full=data.get('fuel_tank_full', False),
            odometer_reading=data.get('odometer_reading', 0),
            fuel_level=data.get('fuel_level', 'Full'),
            damage_noted=data.get('damage_noted', False),
            damage_description=data.get('damage_description'),
            damage_charges=data.get('damage_charges', 0),
            fuel_charges=data.get('fuel_charges', 0),
            late_return_charges=data.get('late_return_charges', 0),
            other_charges=data.get('other_charges', 0),
            charges_description=data.get('charges_description'),
            return_notes=data.get('return_notes'),
            returned_by=current_user.id
        )
        
        db.session.add(vehicle_return)
        
        # Update booking status to completed
        booking.status = BookingStatus.COMPLETED
        
        # Update car status to available if all checks pass
        if vehicle_return.is_checklist_complete():
            if booking.car:
                booking.car.status = CarStatus.AVAILABLE
        
        db.session.commit()
        
        # Log the return
        current_app.logger.info(f"Vehicle return processed for booking {booking.booking_number} by {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Vehicle return processed successfully',
            'return_id': vehicle_return.id,
            'total_charges': vehicle_return.calculate_total_charges()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing vehicle return: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


@admin_bp.route('/settings')
@admin_required
def settings():
    """Admin settings page."""
    from app.models import XeroToken
    
    # Check Xero connection status
    xero_token = XeroToken.query.order_by(XeroToken.created_at.desc()).first()
    xero_connected = xero_token is not None and xero_token.refresh_token is not None
    
    return render_template('admin/settings.html', 
                         xero_connected=xero_connected,
                         xero_token=xero_token)


@admin_bp.route('/xero-settings')
@admin_required
def xero_settings():
    """Xero integration settings page."""
    callback_url = current_app.config.get('XERO_CALLBACK_URL', '')
    return render_template('admin/xero_settings.html', callback_url=callback_url)


# API endpoint for fetching collection photos  
@admin_bp.route('/api/booking/<int:booking_id>/collection-photos', methods=['GET'])
@admin_required
def get_collection_photos(booking_id):
    """Get collection photos for a booking."""
    from app.models import BookingPhoto
    
    try:
        # Get photos from BookingPhoto model
        booking_photos = BookingPhoto.query.filter_by(
            booking_id=booking_id,
            photo_type='pickup'
        ).all()
        
        if booking_photos:
            photos = []
            for photo in booking_photos:
                photos.append({
                    'url': photo.photo_url,
                    'description': photo.description or 'Collection photo',
                    'timestamp': photo.uploaded_at.strftime('%Y-%m-%d %H:%M') if photo.uploaded_at else ''
                })
            
            return jsonify({
                'success': True,
                'photos': photos
            })
        
        return jsonify({
            'success': True,
            'photos': []
        })
            
    except Exception as e:
        current_app.logger.error(f"Error fetching collection photos: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching photos'
        })

