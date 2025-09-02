from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Payment, Booking, PaymentStatus, PaymentMethod
from app.utils.decorators import manager_required
from datetime import datetime

bp = Blueprint('payments', __name__, url_prefix='/payments')


@bp.route('/')
@login_required
@manager_required
def index():
    """List all payments."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = Payment.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=PaymentStatus[status.upper()])
    if search:
        query = query.filter(
            db.or_(
                Payment.transaction_id.contains(search),
                Payment.billing_email.contains(search),
                Payment.billing_name.contains(search)
            )
        )
    
    payments = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Calculate totals
    totals = {
        'all': db.session.query(db.func.sum(Payment.amount)).scalar() or 0,
        'completed': db.session.query(db.func.sum(Payment.amount)).filter_by(
            status=PaymentStatus.COMPLETED).scalar() or 0,
        'pending': db.session.query(db.func.sum(Payment.amount)).filter_by(
            status=PaymentStatus.PENDING).scalar() or 0,
        'refunded': db.session.query(db.func.sum(Payment.refund_amount)).scalar() or 0
    }
    
    return render_template('pages/payments/index.html',
                         payments=payments,
                         statuses=PaymentStatus,
                         totals=totals)


@bp.route('/<int:id>')
@login_required
def view(id):
    """View payment details."""
    payment = Payment.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_manager and payment.user_id != current_user.id:
        flash('You do not have permission to view this payment.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('pages/payments/view.html', payment=payment)


@bp.route('/process/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def process(booking_id):
    """Process payment for a booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check permission
    if not current_user.is_manager and booking.customer_id != current_user.id:
        flash('You do not have permission to process this payment.', 'error')
        return redirect(url_for('bookings.index'))
    
    # Check if payment already exists
    existing_payment = Payment.query.filter_by(
        booking_id=booking.id,
        status=PaymentStatus.COMPLETED
    ).first()
    
    if existing_payment:
        flash('Payment already processed for this booking.', 'info')
        return redirect(url_for('payments.view', id=existing_payment.id))
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            user_id=booking.customer_id,
            amount=booking.total_amount,
            payment_method=PaymentMethod[data['payment_method'].upper()],
            billing_name=data['billing_name'],
            billing_email=data['billing_email'],
            billing_phone=data.get('billing_phone'),
            billing_address=data.get('billing_address'),
            billing_city=data.get('billing_city'),
            billing_state=data.get('billing_state'),
            billing_zip=data.get('billing_zip'),
            billing_country=data.get('billing_country', 'USA'),
            description=f'Payment for booking {booking.booking_number}'
        )
        
        # Generate transaction ID
        payment.generate_transaction_id()
        
        # Process based on payment method
        if payment.payment_method == PaymentMethod.CREDIT_CARD:
            # Simulate credit card processing
            payment.card_last_four = data.get('card_number', '0000')[-4:]
            payment.card_brand = detect_card_brand(data.get('card_number', ''))
            payment.gateway = 'stripe'
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()
            
            # Update booking status
            from app.models.booking import BookingStatus
            booking.status = BookingStatus.CONFIRMED
            
        elif payment.payment_method == PaymentMethod.CASH:
            # Cash payment - mark as pending until confirmed
            payment.status = PaymentStatus.PENDING
            
        else:
            # Other payment methods
            payment.status = PaymentStatus.PROCESSING
        
        db.session.add(payment)
        db.session.commit()
        
        flash(f'Payment {payment.transaction_id} processed successfully!', 'success')
        return redirect(url_for('payments.receipt', id=payment.id))
    
    # Pre-fill billing information from user profile
    billing_info = {
        'billing_name': current_user.full_name,
        'billing_email': current_user.email,
        'billing_phone': current_user.phone,
        'billing_address': current_user.address,
        'billing_city': current_user.city,
        'billing_state': current_user.state,
        'billing_zip': current_user.zip_code
    }
    
    return render_template('pages/payments/process.html',
                         booking=booking,
                         billing_info=billing_info,
                         payment_methods=PaymentMethod)


@bp.route('/<int:id>/receipt')
@login_required
def receipt(id):
    """View payment receipt."""
    payment = Payment.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_manager and payment.user_id != current_user.id:
        flash('You do not have permission to view this receipt.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('pages/payments/receipt.html', payment=payment)


@bp.route('/<int:id>/refund', methods=['GET', 'POST'])
@login_required
@manager_required
def refund(id):
    """Process a refund for a payment."""
    payment = Payment.query.get_or_404(id)
    
    if not payment.can_refund:
        flash('This payment cannot be refunded.', 'error')
        return redirect(url_for('payments.view', id=id))
    
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        reason = request.form.get('reason')
        
        try:
            payment.process_refund(amount, reason)
            db.session.commit()
            flash(f'Refund of ${amount:.2f} processed successfully!', 'success')
            return redirect(url_for('payments.view', id=id))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('payments.refund', id=id))
    
    max_refund = payment.amount - payment.refund_amount
    
    return render_template('pages/payments/refund.html',
                         payment=payment,
                         max_refund=max_refund)


@bp.route('/<int:id>/confirm', methods=['POST'])
@login_required
@manager_required
def confirm(id):
    """Confirm a pending payment."""
    payment = Payment.query.get_or_404(id)
    
    if payment.status != PaymentStatus.PENDING:
        flash('Only pending payments can be confirmed.', 'error')
        return redirect(url_for('payments.view', id=id))
    
    payment.status = PaymentStatus.COMPLETED
    payment.processed_at = datetime.utcnow()
    
    # Update booking status
    if payment.booking:
        from app.models.booking import BookingStatus
        payment.booking.status = BookingStatus.CONFIRMED
    
    db.session.commit()
    flash('Payment confirmed successfully!', 'success')
    return redirect(url_for('payments.view', id=id))


def detect_card_brand(card_number):
    """Detect credit card brand from card number."""
    if not card_number:
        return 'Unknown'
    
    # Remove spaces and non-digits
    card_number = ''.join(filter(str.isdigit, card_number))
    
    if card_number.startswith('4'):
        return 'Visa'
    elif card_number.startswith(('51', '52', '53', '54', '55')):
        return 'Mastercard'
    elif card_number.startswith(('34', '37')):
        return 'American Express'
    elif card_number.startswith('6011'):
        return 'Discover'
    else:
        return 'Other'