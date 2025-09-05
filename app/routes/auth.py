from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Role, BookingStatus
from app.utils.decorators import anonymous_required
import jwt
from datetime import datetime, timedelta
from config import Config

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    """Handle user login."""
    if request.method == 'POST':
        if request.is_json:
            # API login
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            # Form login
            email = request.form.get('email')
            password = request.form.get('password')
            remember_value = request.form.get('remember', '')
            # Coerce remember checkbox to boolean (on/true/1)
            remember = str(remember_value).lower() in ['on', 'true', '1', 'yes']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                if request.is_json:
                    return jsonify({'error': 'Account is deactivated'}), 403
                flash('Your account has been deactivated. Please contact support.', 'error')
                return redirect(url_for('auth.login'))
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if request.is_json:
                # Generate JWT token for API
                token = generate_token(user)
                return jsonify({
                    'token': token,
                    'user': user.to_dict()
                }), 200
            else:
                # Regular login
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                
                # Redirect based on role
                if user.is_admin or user.is_manager:
                    return redirect(next_page or url_for('admin.dashboard'))
                else:
                    return redirect(next_page or url_for('main.index'))
        else:
            if request.is_json:
                return jsonify({'error': 'Invalid email or password'}), 401
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('pages/login.html')


@bp.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """Handle user registration."""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                if request.is_json:
                    return jsonify({'error': f'{field} is required'}), 400
                flash(f'{field.replace("_", " ").title()} is required', 'error')
                return redirect(url_for('auth.register'))
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            if request.is_json:
                return jsonify({'error': 'Email already registered'}), 400
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=data['username']).first():
            if request.is_json:
                return jsonify({'error': 'Username already taken'}), 400
            flash('Username already taken', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=Role.CUSTOMER
        )
        user.set_password(data['password'])
        
        # Add optional fields
        for field in ['address', 'city', 'state', 'zip_code', 'country']:
            if data.get(field):
                setattr(user, field, data[field])
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Registration successful',
                'user': user.to_dict()
            }), 201
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('pages/register.html')


@bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/profile')
@login_required
def profile():
    """View user profile."""
    return render_template('pages/profile.html', user=current_user, BookingStatus=BookingStatus)


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Update user fields
        updateable_fields = ['first_name', 'last_name', 'phone', 'address', 
                           'city', 'state', 'zip_code', 'country', 'license_number',
                           'license_state', 'license_class']
        
        for field in updateable_fields:
            if field in data:  # Update even if empty to allow clearing fields
                setattr(current_user, field, data[field])
        
        # Auto-sync license_state with state if license_state is empty but state is provided
        # This helps users who update their address state but forget to update license state
        if data.get('state') and not data.get('license_state') and not current_user.license_state:
            current_user.license_state = data.get('state')
        
        # Handle date fields separately
        if data.get('date_of_birth'):
            from datetime import datetime
            try:
                current_user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if data.get('license_expiry'):
            from datetime import datetime
            try:
                current_user.license_expiry = datetime.strptime(data['license_expiry'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Handle password change
        if data.get('new_password'):
            if not current_user.check_password(data.get('current_password', '')):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('auth.edit_profile'))
            current_user.set_password(data['new_password'])
        
        # Ensure the user is in the session
        db.session.add(current_user)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
        # Check if there was a pending booking and redirect back if profile is now complete
        from flask import session
        if 'pending_booking_car' in session and current_user.has_complete_driver_details():
            car_id = session.pop('pending_booking_car')
            flash('Your profile is now complete! You can proceed with your booking.', 'info')
            return redirect(url_for('bookings.create', car_id=car_id))
        
        return redirect(url_for('auth.profile'))
    
    return render_template('pages/edit_profile.html', user=current_user)


def generate_token(user):
    """Generate JWT token for API authentication."""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role.value,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')


def verify_token(token):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None