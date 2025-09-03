from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Booking, Car, User, Payment, BookingStatus, PaymentStatus, Role
from app.utils.decorators import manager_required
from datetime import datetime

bp = Blueprint('bookings', __name__, url_prefix='/bookings')


@bp.route('/')
@login_required
def index():
    """List all bookings for the current user or all bookings for admin."""
    page = request.args.get('page', 1, type=int)
    
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
@login_required
def create():
    """Create a new booking."""
    # Check if user has complete driver license and address details
    if not current_user.has_complete_driver_details():
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
        total_days = (return_date - pickup_date).days
        if total_days < 1:
            total_days = 1
        
        subtotal = car.calculate_rental_cost(total_days)
        tax_amount = subtotal * 0.1  # 10% tax
        total_amount = subtotal + tax_amount
        
        # Create booking
        booking = Booking(
            customer_id=current_user.id,
            car_id=car.id,
            pickup_date=pickup_date,
            return_date=return_date,
            pickup_location=data.get('pickup_location', 'Main Office'),
            return_location=data.get('return_location', 'Main Office'),
            daily_rate=car.daily_rate,
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
    
    # Get payment history
    payments = Payment.query.filter_by(booking_id=booking.id).all()
    
    return render_template('pages/bookings/view.html', 
                         booking=booking, 
                         payments=payments)


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
    if current_user.role not in [Role.ADMIN, Role.MANAGER]:
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