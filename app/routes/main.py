from flask import Blueprint, render_template, jsonify, current_app
from app.models import Car, Booking, User, Role
from sqlalchemy import func
from app import db

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page."""
    try:
        # Get featured cars
        featured_cars = Car.query.filter_by(is_active=True).limit(6).all()
        
        # Get statistics with proper enum usage
        stats = {
            'total_cars': Car.query.filter_by(is_active=True).count(),
            'total_bookings': Booking.query.count(),
            'happy_customers': User.query.filter_by(role=Role.CUSTOMER).count(),
            'years_experience': 10
        }
        
        return render_template('pages/home.html', 
                             featured_cars=featured_cars,
                             stats=stats)
    except Exception as e:
        current_app.logger.error(f"Error loading home page: {str(e)}")
        # Return with default values if there's an error
        return render_template('pages/home.html', 
                             featured_cars=[],
                             stats={
                                 'total_cars': 0,
                                 'total_bookings': 0,
                                 'happy_customers': 0,
                                 'years_experience': 10
                             })


@bp.route('/about')
def about():
    """About page."""
    return render_template('pages/about.html')


@bp.route('/buy-car')
def buy_car():
    """Buy Car page."""
    return render_template('pages/buy_car.html')


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page."""
    from flask import request, flash
    
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you would typically send an email or save to database
        # For now, just flash a success message
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return render_template('pages/contact.html')
    
    return render_template('pages/contact.html')


@bp.route('/terms')
def terms():
    """Terms and conditions page."""
    return render_template('pages/terms.html')


@bp.route('/privacy')
def privacy():
    """Privacy policy page."""
    return render_template('pages/privacy.html')


@bp.route('/faq')
def faq():
    """FAQ page."""
    faqs = [
        {
            'question': 'How do I book a car?',
            'answer': 'Simply browse our fleet, select your desired car, choose your rental dates, and complete the booking process.'
        },
        {
            'question': 'What documents do I need?',
            'answer': 'You need a valid driver\'s license, a credit card, and proof of identity.'
        },
        {
            'question': 'Can I cancel my booking?',
            'answer': 'Yes, you can cancel your booking up to 24 hours before the pickup time for a full refund.'
        },
        {
            'question': 'Is insurance included?',
            'answer': 'Basic insurance is included. Additional coverage options are available at checkout.'
        },
        {
            'question': 'What is the minimum age to rent?',
            'answer': 'The minimum age is 21 years old with a valid driver\'s license held for at least 1 year.'
        }
    ]
    return render_template('pages/faq.html', faqs=faqs)


@bp.route('/fleet')
def fleet():
    """Fleet overview page."""
    from app.models import CarCategory
    
    # Get cars grouped by category
    cars_by_category = {}
    for category in CarCategory:
        cars = Car.query.filter_by(category=category, is_active=True).all()
        if cars:
            cars_by_category[category.value] = cars
    
    return render_template('pages/fleet.html', cars_by_category=cars_by_category)


@bp.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('errors/404.html'), 404


@bp.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    from app import db
    db.session.rollback()
    return render_template('errors/500.html'), 500