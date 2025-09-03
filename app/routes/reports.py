from flask import Blueprint, render_template, request, send_file, jsonify, current_app
from flask_login import login_required
from app import db
from app.models import Booking, Payment, Car, User, Driver, Role
from app.utils.decorators import manager_required
from datetime import datetime, timedelta
from sqlalchemy import func
import io
import csv

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/')
@login_required
@manager_required
def index():
    """Reports dashboard."""
    return render_template('pages/reports/index.html')


@bp.route('/revenue')
@login_required
@manager_required
def revenue():
    """Revenue report."""
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = datetime.utcnow().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get revenue data
    revenue_query = db.session.query(
        func.date(Payment.created_at).label('date'),
        func.sum(Payment.amount).label('revenue'),
        func.count(Payment.id).label('transaction_count')
    ).filter(
        Payment.status == 'completed',
        func.date(Payment.created_at) >= start_date,
        func.date(Payment.created_at) <= end_date
    ).group_by(func.date(Payment.created_at)).all()
    
    # Calculate totals
    total_revenue = sum(r.revenue for r in revenue_query)
    total_transactions = sum(r.transaction_count for r in revenue_query)
    average_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
    
    # Get revenue by payment method
    revenue_by_method = db.session.query(
        Payment.payment_method,
        func.sum(Payment.amount).label('amount'),
        func.count(Payment.id).label('count')
    ).filter(
        Payment.status == 'completed',
        func.date(Payment.created_at) >= start_date,
        func.date(Payment.created_at) <= end_date
    ).group_by(Payment.payment_method).all()
    
    return render_template('pages/reports/revenue.html',
                         revenue_data=revenue_query,
                         revenue_by_method=revenue_by_method,
                         total_revenue=total_revenue,
                         total_transactions=total_transactions,
                         average_transaction=average_transaction,
                         start_date=start_date,
                         end_date=end_date)


@bp.route('/bookings')
@login_required
@manager_required
def bookings():
    """Bookings report."""
    # Get filters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    
    query = Booking.query
    
    if start_date:
        query = query.filter(Booking.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Booking.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
    if status:
        query = query.filter_by(status=status)
    
    bookings_data = query.all()
    
    # Calculate statistics
    stats = {
        'total_bookings': len(bookings_data),
        'completed': len([b for b in bookings_data if b.status.value == 'completed']),
        'cancelled': len([b for b in bookings_data if b.status.value == 'cancelled']),
        'in_progress': len([b for b in bookings_data if b.status.value == 'in_progress']),
        'total_revenue': sum(b.total_amount for b in bookings_data if b.status.value == 'completed')
    }
    
    # Get bookings by car category
    bookings_by_category = db.session.query(
        Car.category,
        func.count(Booking.id).label('count'),
        func.sum(Booking.total_amount).label('revenue')
    ).join(Car).filter(
        Booking.id.in_([b.id for b in bookings_data])
    ).group_by(Car.category).all()
    
    return render_template('pages/reports/bookings.html',
                         bookings=bookings_data[:100],  # Limit display
                         stats=stats,
                         bookings_by_category=bookings_by_category)


@bp.route('/fleet-utilization')
@login_required
@manager_required
def fleet_utilization():
    """Fleet utilization report."""
    # Get all cars with their booking statistics
    cars_data = []
    
    for car in Car.query.filter_by(is_active=True).all():
        # Calculate utilization for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        bookings = Booking.query.filter(
            Booking.car_id == car.id,
            Booking.created_at >= thirty_days_ago,
            Booking.status.in_(['completed', 'in_progress'])
        ).all()
        
        total_days_booked = sum(b.total_days for b in bookings)
        utilization_rate = (total_days_booked / 30) * 100
        revenue = sum(b.total_amount for b in bookings if b.status.value == 'completed')
        
        cars_data.append({
            'car': car,
            'bookings_count': len(bookings),
            'days_booked': total_days_booked,
            'utilization_rate': min(utilization_rate, 100),
            'revenue': revenue
        })
    
    # Sort by utilization rate
    cars_data.sort(key=lambda x: x['utilization_rate'], reverse=True)
    
    # Calculate overall statistics
    overall_stats = {
        'total_cars': len(cars_data),
        'average_utilization': sum(c['utilization_rate'] for c in cars_data) / len(cars_data) if cars_data else 0,
        'total_revenue': sum(c['revenue'] for c in cars_data),
        'highly_utilized': len([c for c in cars_data if c['utilization_rate'] > 70]),
        'underutilized': len([c for c in cars_data if c['utilization_rate'] < 30])
    }
    
    return render_template('pages/reports/fleet_utilization.html',
                         cars_data=cars_data,
                         overall_stats=overall_stats)


@bp.route('/customers')
@login_required
@manager_required
def customers():
    """Customer analytics report."""
    try:
        # Get top customers by revenue
        top_customers = db.session.query(
            User,
            func.count(Booking.id).label('booking_count'),
            func.sum(Booking.total_amount).label('total_spent'),
            func.avg(Booking.total_amount).label('avg_booking_value')
        ).join(Booking, User.id == Booking.customer_id).filter(
            Booking.status == 'completed'
        ).group_by(User.id).order_by(
            func.sum(Booking.total_amount).desc()
        ).limit(20).all()
        
        # Get new customers (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_customers = User.query.filter(
            User.role == Role.CUSTOMER,
            User.created_at >= thirty_days_ago
        ).count()
        
        # Get customer retention data
        total_customers = User.query.filter_by(role=Role.CUSTOMER).count()
        repeat_customers = 0
        
        try:
            repeat_customers = db.session.query(
                func.count(func.distinct(Booking.customer_id))
            ).filter(
                db.exists().where(
                    db.and_(
                        Booking.customer_id == User.id,
                        Booking.id != db.session.query(func.min(Booking.id)).filter(
                            Booking.customer_id == User.id
                        ).scalar_subquery()
                    )
                )
            ).scalar() or 0
        except Exception as e:
            current_app.logger.error(f"Error calculating repeat customers: {str(e)}")
            repeat_customers = 0
        
        retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        return render_template('pages/reports/customers.html',
                             top_customers=top_customers,
                             new_customers=new_customers,
                             total_customers=total_customers,
                             repeat_customers=repeat_customers,
                             retention_rate=retention_rate)
    except Exception as e:
        current_app.logger.error(f"Error generating customer report: {str(e)}")
        # Return with default values if there's an error
        return render_template('pages/reports/customers.html',
                             top_customers=[],
                             new_customers=0,
                             total_customers=0,
                             repeat_customers=0,
                             retention_rate=0)


@bp.route('/export/<report_type>')
@login_required
@manager_required
def export(report_type):
    """Export report data to CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'bookings':
        # Export bookings data
        writer.writerow(['Booking Number', 'Customer', 'Car', 'Pickup Date', 
                        'Return Date', 'Total Amount', 'Status'])
        
        bookings = Booking.query.all()
        for booking in bookings:
            writer.writerow([
                booking.booking_number,
                booking.customer.full_name if booking.customer else '',
                booking.car.full_name if booking.car else '',
                booking.pickup_date.strftime('%Y-%m-%d') if booking.pickup_date else '',
                booking.return_date.strftime('%Y-%m-%d') if booking.return_date else '',
                booking.total_amount,
                booking.status.value
            ])
    
    elif report_type == 'payments':
        # Export payments data
        writer.writerow(['Transaction ID', 'Date', 'Amount', 'Method', 
                        'Status', 'Customer'])
        
        payments = Payment.query.all()
        for payment in payments:
            writer.writerow([
                payment.transaction_id,
                payment.created_at.strftime('%Y-%m-%d %H:%M') if payment.created_at else '',
                payment.amount,
                payment.payment_method.value,
                payment.status.value,
                payment.user.full_name if payment.user else ''
            ])
    
    elif report_type == 'fleet':
        # Export fleet data
        writer.writerow(['License Plate', 'Make', 'Model', 'Year', 
                        'Category', 'Status', 'Daily Rate'])
        
        cars = Car.query.all()
        for car in cars:
            writer.writerow([
                car.license_plate,
                car.make,
                car.model,
                car.year,
                car.category.value,
                car.status.value,
                car.daily_rate
            ])
    
    else:
        return "Invalid report type", 404
    
    # Create response
    output.seek(0)
    response = send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{report_type}_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )
    
    return response