from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app.models import User, Car, Booking, Payment, Driver
from app.utils.decorators import admin_required, manager_required
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
@login_required
@manager_required
def index():
    """Admin dashboard main page."""
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'total_cars': Car.query.count(),
        'total_bookings': Booking.query.count(),
        'total_revenue': db.session.query(func.sum(Payment.amount)).filter_by(status='completed').scalar() or 0,
        'active_bookings': Booking.query.filter_by(status='in_progress').count(),
        'available_cars': Car.query.filter_by(status='available').count(),
        'total_drivers': Driver.query.count(),
        'pending_bookings': Booking.query.filter_by(status='pending').count()
    }
    
    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get revenue chart data (last 7 days)
    revenue_data = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        daily_revenue = db.session.query(func.sum(Payment.amount)).filter(
            func.date(Payment.created_at) == date.date(),
            Payment.status == 'completed'
        ).scalar() or 0
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    revenue_data.reverse()
    
    # Get booking chart data (last 7 days)
    booking_data = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        daily_bookings = Booking.query.filter(
            func.date(Booking.created_at) == date.date()
        ).count()
        booking_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': daily_bookings
        })
    booking_data.reverse()
    
    return render_template('pages/dashboard/index.html',
                         stats=stats,
                         recent_bookings=recent_bookings,
                         revenue_data=revenue_data,
                         booking_data=booking_data)


@bp.route('/payments')
@login_required
@manager_required
def payments_history():
    """Record of all payments received."""
    page = request.args.get('page', 1, type=int)
    payments = Payment.query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('pages/dashboard/payments.html', payments=payments)


@bp.route('/analytics')
@login_required
@manager_required
def analytics():
    """Analytics and reports page."""
    from app.models import CarCategory, BookingStatus
    
    # Get booking statistics by status
    booking_stats = {}
    for status in BookingStatus:
        count = Booking.query.filter_by(status=status).count()
        booking_stats[status.value] = count
    
    # Get car utilization by category
    car_utilization = {}
    for category in CarCategory:
        cars = Car.query.filter_by(category=category).all()
        if cars:
            total = len(cars)
            available = len([c for c in cars if c.status.value == 'available'])
            utilization = ((total - available) / total * 100) if total > 0 else 0
            car_utilization[category.value] = {
                'total': total,
                'available': available,
                'utilization': round(utilization, 1)
            }
    
    # Get top customers
    top_customers = db.session.query(
        User,
        func.count(Booking.id).label('booking_count'),
        func.sum(Payment.amount).label('total_spent')
    ).join(
        Booking, User.id == Booking.customer_id
    ).join(
        Payment, Booking.id == Payment.booking_id
    ).group_by(User.id).order_by(
        func.sum(Payment.amount).desc()
    ).limit(10).all()
    
    # Get monthly revenue (last 12 months)
    monthly_revenue = []
    for i in range(12):
        date = datetime.utcnow() - timedelta(days=30*i)
        month_revenue = db.session.query(func.sum(Payment.amount)).filter(
            func.extract('year', Payment.created_at) == date.year,
            func.extract('month', Payment.created_at) == date.month,
            Payment.status == 'completed'
        ).scalar() or 0
        monthly_revenue.append({
            'month': date.strftime('%B %Y'),
            'revenue': float(month_revenue)
        })
    monthly_revenue.reverse()
    
    return render_template('pages/dashboard/analytics.html',
                         booking_stats=booking_stats,
                         car_utilization=car_utilization,
                         top_customers=top_customers,
                         monthly_revenue=monthly_revenue)


@bp.route('/settings')
@login_required
@admin_required
def settings():
    """System settings page."""
    return render_template('pages/dashboard/settings.html')


@bp.route('/profile')
@login_required
@manager_required
def profile():
    """Admin profile page."""
    return render_template('pages/dashboard/profile.html', user=current_user)


from app import db