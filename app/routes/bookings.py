from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Booking, Car, User, Payment, BookingStatus, PaymentStatus, Role, VehicleReturn, VehiclePhoto, PhotoType
from app.utils.decorators import manager_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from math import ceil

bp = Blueprint('bookings', __name__, url_prefix='/bookings')


@bp.route('/')
@login_required
def index():
    """List all bookings for the current user or all bookings for admin."""
    page = request.args.get('page', 1, type=int)
    
    # Auto-update booking statuses for confirmed bookings past pickup date
    confirmed_bookings = Booking.query.filter_by(status=BookingStatus.CONFIRMED).all()
    for booking in confirmed_bookings:
        if booking.auto_update_status():
            # Also update car status when auto-transitioning
            if booking.car:
                from app.models.car import CarStatus
                booking.car.status = CarStatus.BOOKED
    db.session.commit()
    
    if current_user.is_manager:
        # Admin sees all bookings
        bookings = Booking.query.order_by(Booking.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False)
    else:
        # Regular user sees only their bookings
        bookings = Booking.query.filter_by(customer_id=current_user.id).order_by(
            Booking.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('pages/bookings/index.html', bookings=bookings)


@bp.route('/new', methods=['GET', 'POST'])
def create():
    """Create a new booking."""
    # Allow guests to select dates and see total, require login only to confirm
    if not current_user.is_authenticated:
        if request.method == 'POST':
            flash('Please login to confirm booking.', 'info')
            return redirect(url_for('auth.login', next=url_for('bookings.create', car_id=request.form.get('car_id'))))
    else:
        # Only enforce profile completion for logged-in users when confirming
        if request.method == 'POST' and not current_user.has_complete_driver_details():
            missing_details = current_user.get_missing_details()
            flash('⚠️ You cannot book a car without completing your driver profile. Please provide the following information:', 'danger')
            for detail in missing_details:
                flash(f'• {detail}', 'danger')
            # Store the intended car_id in session to redirect back after profile completion
            if request.args.get('car_id'):
                from flask import session
                session['pending_booking_car'] = request.args.get('car_id')
            return redirect(url_for('auth.edit_profile') + '#license')
    
    if request.method == 'POST':
        # Double-check profile completion in case of direct POST manipulation
        if not current_user.has_complete_driver_details():
            flash('⚠️ Profile validation failed. Please complete your driver details first.', 'danger')
            return redirect(url_for('auth.edit_profile') + '#license')
        
        data = request.form.to_dict()
        
        # Validate car availability
        car = Car.query.get_or_404(data['car_id'])
        if not car.is_available:
            flash('This car is not available for booking.', 'error')
            return redirect(url_for('bookings.create'))
        
        # Parse dates - handle both formats (with T separator and space separator)
        pickup_date_str = data['pickup_date'].replace('T', ' ') if 'T' in data['pickup_date'] else data['pickup_date']
        return_date_str = data['return_date'].replace('T', ' ') if 'T' in data['return_date'] else data['return_date']
        
        pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d %H:%M')
        return_date = datetime.strptime(return_date_str, '%Y-%m-%d %H:%M')
        
        # Calculate rental details
        total_days = ceil((return_date - pickup_date).total_seconds() / (60 * 60 * 24))
        if total_days < 7:
            flash('Minimum rental period is 7 days. Please adjust your dates.', 'danger')
            return redirect(url_for('bookings.create', car_id=car.id))
        
        subtotal = car.calculate_rental_cost(total_days)
        tax_amount = subtotal * 0.1  # 10% GST
        total_amount = subtotal + tax_amount
        
        # Create booking
        booking = Booking(
            customer_id=current_user.id,
            car_id=car.id,
            pickup_date=pickup_date,
            return_date=return_date,
            pickup_location=data.get('pickup_location', 'Main Office'),
            return_location=data.get('return_location', 'Main Office'),
            # daily_rate=car.daily_rate,  # Deprecated: using weekly-based pricing
            total_days=total_days,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status=BookingStatus.PENDING,
            customer_notes=data.get('customer_notes'),
            with_driver=data.get('with_driver') == 'on',
            insurance_opted=data.get('insurance_opted') == 'on',
            gps_opted=data.get('gps_opted') == 'on'
        )
        
        # Generate booking number
        booking.generate_booking_number()
        
        # Update car status
        from app.models.car import CarStatus
        car.status = CarStatus.BOOKED
        
        # If a license document was uploaded at booking time, store it
        try:
            license_file = request.files.get('license_document')
        except Exception:
            license_file = None

        if license_file and getattr(license_file, 'filename', None):
            try:
                from app.services.storage import get_storage
                storage = get_storage()
                filename = secure_filename(license_file.filename)
                key = storage.generate_key('licenses', filename)
                url = storage.upload_fileobj(license_file, key, content_type=license_file.mimetype)
                booking.license_document_url = url
            except Exception as e:
                # Non-fatal: allow booking to proceed even if license upload fails
                flash(f'License upload failed: {str(e)}', 'warning')

        db.session.add(booking)
        db.session.commit()
        
        flash(f'Booking {booking.booking_number} created successfully!', 'success')
        return redirect(url_for('bookings.view', id=booking.id))
    
    # Check if a specific car was requested
    selected_car = None
    car_id = request.args.get('car_id')
    if car_id:
        selected_car = Car.query.get(car_id)
    
    # Get available cars
    from app.models.car import CarStatus
    available_cars = Car.query.filter_by(status=CarStatus.AVAILABLE, is_active=True).all()
    
    # If a car was selected but not in available list, add it (for pre-selection)
    if selected_car and selected_car not in available_cars and selected_car.is_active:
        available_cars.append(selected_car)
    
    return render_template('pages/bookings/create.html', 
                         cars=available_cars,
                         selected_car=selected_car)


@bp.route('/<int:id>')
@login_required
def view(id):
    """View booking details."""
    booking = Booking.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_manager and booking.customer_id != current_user.id:
        flash('You do not have permission to view this booking.', 'error')
        return redirect(url_for('bookings.index'))
    
    # Auto-update status if needed
    if booking.auto_update_status():
        if booking.car:
            from app.models.car import CarStatus
            booking.car.status = CarStatus.BOOKED
        db.session.commit()
        flash('Booking status automatically updated to In Progress as pickup date has passed.', 'info')
    
    # Get payment history
    payments = Payment.query.filter_by(booking_id=booking.id).all()
    
    # Get pickup photos if any
    pickup_photos = VehiclePhoto.query.filter_by(
        booking_id=booking.id, 
        photo_type=PhotoType.PICKUP
    ).all()
    
    return render_template('pages/bookings/view.html', 
                         booking=booking, 
                         payments=payments,
                         pickup_photos=pickup_photos)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit booking details."""
    booking = Booking.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_manager:
        flash('Only managers can edit bookings.', 'error')
        return redirect(url_for('bookings.view', id=id))
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Update booking fields - handle both date formats
        if data.get('pickup_date'):
            pickup_date_str = data['pickup_date'].replace('T', ' ') if 'T' in data['pickup_date'] else data['pickup_date']
            booking.pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d %H:%M')
        if data.get('return_date'):
            return_date_str = data['return_date'].replace('T', ' ') if 'T' in data['return_date'] else data['return_date']
            booking.return_date = datetime.strptime(return_date_str, '%Y-%m-%d %H:%M')
        
        booking.pickup_location = data.get('pickup_location', booking.pickup_location)
        booking.return_location = data.get('return_location', booking.return_location)
        booking.admin_notes = data.get('admin_notes')
        
        # Recalculate if dates changed
        if data.get('pickup_date') or data.get('return_date'):
            total_days = (booking.return_date - booking.pickup_date).days
            if total_days < 1:
                total_days = 1
            booking.total_days = total_days
            booking.subtotal = booking.car.calculate_rental_cost(total_days)
            booking.total_amount = booking.subtotal + booking.tax_amount - booking.discount_amount
        
        db.session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('bookings.view', id=id))
    
    return render_template('pages/bookings/edit.html', booking=booking)


@bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """Cancel a booking."""
    from flask import jsonify
    
    booking = Booking.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_manager and booking.customer_id != current_user.id:
        return jsonify({'success': False, 'message': 'You do not have permission to cancel this booking.'}), 403
    
    if not booking.can_cancel:
        return jsonify({'success': False, 'message': 'This booking cannot be cancelled.'}), 400
    
    try:
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = request.form.get('reason', 'Customer requested cancellation')
        
        # Calculate cancellation fee if applicable
        hours_until_pickup = (booking.pickup_date - datetime.utcnow()).total_seconds() / 3600
        if hours_until_pickup < 24:
            booking.cancellation_fee = booking.total_amount * 0.25  # 25% cancellation fee
        
        # Update car status
        if booking.car:
            from app.models.car import CarStatus
            booking.car.status = CarStatus.AVAILABLE
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/<int:id>/confirm', methods=['POST'])
@login_required
@manager_required
def confirm(id):
    """Confirm a pending booking."""
    booking = Booking.query.get_or_404(id)
    
    if booking.status != BookingStatus.PENDING:
        flash('Only pending bookings can be confirmed.', 'error')
        return redirect(url_for('bookings.view', id=id))
    
    booking.status = BookingStatus.CONFIRMED
    db.session.commit()
    
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('bookings.view', id=id))


@bp.route('/<int:id>/start', methods=['POST'])
@login_required
@manager_required
def start(id):
    """Mark a booking as in progress when vehicle is picked up."""
    booking = Booking.query.get_or_404(id)
    
    if booking.status != BookingStatus.CONFIRMED:
        flash('Only confirmed bookings can be started.', 'error')
        return redirect(url_for('bookings.view', id=id))
    
    booking.status = BookingStatus.IN_PROGRESS
    booking.actual_pickup_date = datetime.utcnow()
    
    # Update car status
    if booking.car:
        from app.models.car import CarStatus
        booking.car.status = CarStatus.BOOKED
    
    db.session.commit()
    
    flash('Vehicle pickup recorded successfully! Booking is now in progress.', 'success')
    return redirect(url_for('bookings.view', id=id))


@bp.route('/<int:id>/complete', methods=['POST'])
@login_required
@manager_required
def complete(id):
    """Mark a booking as completed."""
    booking = Booking.query.get_or_404(id)
    
    if booking.status != BookingStatus.IN_PROGRESS:
        flash('Only in-progress bookings can be completed.', 'error')
        return redirect(url_for('bookings.view', id=id))
    
    booking.status = BookingStatus.COMPLETED
    booking.actual_return_date = datetime.utcnow()
    
    # Update car status
    if booking.car:
        from app.models.car import CarStatus
        booking.car.status = CarStatus.AVAILABLE
    
    db.session.commit()
    flash('Booking completed successfully!', 'success')
    return redirect(url_for('bookings.view', id=id))


@bp.route('/<int:booking_id>/send-invoice')
@login_required
def send_invoice_page(booking_id):
    """Display the send invoice page for a booking."""
    # Check if user is admin or manager
    if current_user.role != Role.ADMIN:
        flash('You do not have permission to send invoices.', 'error')
        return redirect(url_for('bookings.view', id=booking_id))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if booking has a customer
    if not booking.customer:
        flash('Cannot send invoice: No customer associated with this booking.', 'error')
        return redirect(url_for('bookings.view', id=booking_id))
    
    # Check if customer has email
    if not booking.customer.email:
        flash('Cannot send invoice: Customer does not have an email address.', 'error')
        return redirect(url_for('bookings.view', id=booking_id))
    
    return render_template('admin/send_invoice.html', booking=booking)


@bp.route('/<int:booking_id>/view')
@login_required
def view_booking(booking_id):
    """View a specific booking details."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user has permission to view this booking
    if not current_user.is_manager and booking.customer_id != current_user.id:
        flash('You do not have permission to view this booking.', 'error')
        return redirect(url_for('bookings.index'))
    
    return render_template('pages/bookings/view.html', booking=booking)


@bp.route('/<int:id>/return', methods=['GET', 'POST'])
@login_required
@manager_required
def process_return(id):
    """Process vehicle return with checklist."""
    booking = Booking.query.get_or_404(id)
    
    # Check if booking is in progress
    if booking.status != BookingStatus.IN_PROGRESS:
        flash('Only in-progress bookings can be returned.', 'error')
        return redirect(url_for('bookings.view', id=id))
    
    # Check if return already exists
    existing_return = VehicleReturn.query.filter_by(booking_id=id).first()
    if existing_return:
        flash('Return has already been processed for this booking.', 'warning')
        return redirect(url_for('bookings.view', id=id))
    
    if request.method == 'POST':
        try:
            # Create vehicle return record
            vehicle_return = VehicleReturn(
                booking_id=booking.id,
                bond_returned=request.form.get('bond_returned') == 'on',
                all_payments_received=request.form.get('all_payments_received') == 'on',
                car_in_good_condition=request.form.get('car_in_good_condition') == 'on',
                fuel_tank_full=request.form.get('fuel_tank_full') == 'on',
                odometer_reading=int(request.form.get('odometer_reading', 0)),
                fuel_level=request.form.get('fuel_level', 'Full'),
                damage_noted=request.form.get('damage_noted') == 'on',
                damage_description=request.form.get('damage_description'),
                damage_charges=float(request.form.get('damage_charges', 0)),
                fuel_charges=float(request.form.get('fuel_charges', 0)),
                late_return_charges=float(request.form.get('late_return_charges', 0)),
                other_charges=float(request.form.get('other_charges', 0)),
                charges_description=request.form.get('charges_description'),
                return_notes=request.form.get('return_notes'),
                returned_by=current_user.id,
                return_date=datetime.utcnow()
            )
            
            # Update booking status
            booking.status = BookingStatus.COMPLETED
            booking.actual_return_date = datetime.utcnow()
            
            # Update car status and odometer
            if booking.car:
                from app.models.car import CarStatus
                booking.car.status = CarStatus.AVAILABLE
                booking.car.current_odometer = vehicle_return.odometer_reading
                booking.car.mileage = vehicle_return.odometer_reading  # Update mileage as well
            
            # Add any additional charges to booking
            total_additional_charges = vehicle_return.calculate_total_charges()
            if total_additional_charges > 0:
                booking.additional_charges = (booking.additional_charges or 0) + total_additional_charges
                booking.total_amount = booking.subtotal + booking.tax_amount - booking.discount_amount + booking.additional_charges
            
            db.session.add(vehicle_return)
            db.session.commit()
            
            flash(f'Vehicle return processed successfully for booking {booking.booking_number}!', 'success')
            
            # Check if all checklist items are complete
            if not vehicle_return.is_checklist_complete():
                flash('⚠️ Warning: Not all checklist items were marked as complete. Please review.', 'warning')
            
            return redirect(url_for('bookings.view', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing return: {str(e)}', 'error')
            return redirect(url_for('bookings.process_return', id=id))
    
    # Calculate any late fees
    late_fees = 0
    days_late = 0
    if booking.return_date < datetime.utcnow():
        days_late = (datetime.utcnow() - booking.return_date).days
        late_fees = days_late * booking.daily_rate * 1.5  # 150% of daily rate for late fees
    
    # Get pickup photos for comparison
    pickup_photos = VehiclePhoto.query.filter_by(
        booking_id=booking.id,
        photo_type=PhotoType.PICKUP
    ).all()
    
    return render_template('pages/bookings/return.html', 
                         booking=booking,
                         late_fees=late_fees,
                         days_late=days_late,
                         pickup_photos=pickup_photos)


@bp.route('/<int:id>/return/view')
@login_required
def view_return(id):
    """View vehicle return details."""
    booking = Booking.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_manager and booking.customer_id != current_user.id:
        flash('You do not have permission to view this return.', 'error')
        return redirect(url_for('bookings.index'))
    
    vehicle_return = VehicleReturn.query.filter_by(booking_id=id).first()
    if not vehicle_return:
        flash('No return record found for this booking.', 'error')
        return redirect(url_for('bookings.view', id=id))
    
    return render_template('pages/bookings/return_view.html', 
                         booking=booking,
                         vehicle_return=vehicle_return)


@bp.route('/<int:id>/photos/upload', methods=['GET', 'POST'])
@login_required
@manager_required
def upload_photos(id):
    """Upload photos for vehicle condition."""
    booking = Booking.query.get_or_404(id)
    
    if request.method == 'POST':
        photo_type = request.form.get('photo_type', 'pickup')
        photos = request.files.getlist('photos')
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join('static', 'uploads', 'vehicle_photos', str(booking.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_count = 0
        for photo in photos:
            if photo and photo.filename:
                # Secure the filename
                filename = secure_filename(photo.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(upload_dir, filename)
                
                # Save the file
                photo.save(filepath)
                
                # Create database record
                vehicle_photo = VehiclePhoto(
                    booking_id=booking.id,
                    photo_url=f"/{filepath}",
                    photo_type=PhotoType.PICKUP if photo_type == 'pickup' else PhotoType.RETURN,
                    caption=request.form.get(f'caption_{uploaded_count}', ''),
                    angle=request.form.get(f'angle_{uploaded_count}', ''),
                    uploaded_by=current_user.id
                )
                db.session.add(vehicle_photo)
                uploaded_count += 1
        
        if uploaded_count > 0:
            db.session.commit()
            flash(f'{uploaded_count} photo(s) uploaded successfully!', 'success')
        else:
            flash('No photos were uploaded.', 'warning')
        
        return redirect(url_for('bookings.view', id=id))
    
    return render_template('pages/bookings/upload_photos.html', booking=booking)


@bp.route('/<int:id>/photos')
@login_required
def view_photos(id):
    """View all photos for a booking."""
    booking = Booking.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_manager and booking.customer_id != current_user.id:
        flash('You do not have permission to view these photos.', 'error')
        return redirect(url_for('bookings.index'))
    
    pickup_photos = VehiclePhoto.query.filter_by(
        booking_id=booking.id,
        photo_type=PhotoType.PICKUP
    ).all()
    
    return_photos = VehiclePhoto.query.filter_by(
        booking_id=booking.id,
        photo_type=PhotoType.RETURN
    ).all()
    
    return render_template('pages/bookings/view_photos.html', 
                         booking=booking,
                         pickup_photos=pickup_photos,
                         return_photos=return_photos)


@bp.route('/<int:id>/receipt')
@login_required
def receipt(id):
    """Redirect to the payment receipt for this booking."""
    booking = Booking.query.get_or_404(id)
    
    # Permission check
    if not current_user.is_manager and booking.customer_id != current_user.id:
        flash('You do not have permission to view this receipt.', 'error')
        return redirect(url_for('bookings.view', id=id))
    
    # Find the most recent completed payment for this booking
    payment = (Payment.query
               .filter_by(booking_id=booking.id)
               .filter(Payment.status == PaymentStatus.COMPLETED)
               .order_by(Payment.created_at.desc())
               .first())
    
    if not payment:
        flash('No completed payment found for this booking. Receipt unavailable.', 'warning')
        return redirect(url_for('bookings.view', id=id))
    
    return redirect(url_for('payments.receipt', id=payment.id))