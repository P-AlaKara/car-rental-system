from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import User, Role, Booking
from app.utils.decorators import admin_required
from werkzeug.security import generate_password_hash

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/')
@login_required
@admin_required
def index():
    """List all users."""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role')
    search = request.args.get('search')
    
    query = User.query
    
    # Apply filters
    if role:
        query = query.filter_by(role=Role[role.upper()])
    if search:
        query = query.filter(
            db.or_(
                User.email.contains(search),
                User.username.contains(search),
                User.first_name.contains(search),
                User.last_name.contains(search)
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('pages/users/index.html', 
                         users=users,
                         roles=Role)


@bp.route('/<int:id>')
@login_required
@admin_required
def view(id):
    """View user details."""
    user = User.query.get_or_404(id)
    
    # Get user statistics
    stats = {
        'total_bookings': Booking.query.filter_by(customer_id=user.id).count(),
        'active_bookings': Booking.query.filter_by(
            customer_id=user.id, status='in_progress').count(),
        'completed_bookings': Booking.query.filter_by(
            customer_id=user.id, status='completed').count(),
        'total_spent': db.session.query(
            db.func.sum(Booking.total_amount)
        ).filter_by(customer_id=user.id, status='completed').scalar() or 0
    }
    
    # Get recent bookings
    recent_bookings = Booking.query.filter_by(customer_id=user.id).order_by(
        Booking.created_at.desc()).limit(5).all()
    
    return render_template('pages/users/view.html',
                         user=user,
                         stats=stats,
                         recent_bookings=recent_bookings)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create a new user."""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            flash('Email already registered', 'error')
            return redirect(url_for('users.create'))
        
        if User.query.filter_by(username=data['username']).first():
            flash('Username already taken', 'error')
            return redirect(url_for('users.create'))
        
        # Create new user
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=Role[data.get('role', 'CUSTOMER').upper()],
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            is_active=data.get('is_active') == 'on',
            is_verified=data.get('is_verified') == 'on'
        )
        
        # Set password
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} created successfully!', 'success')
        return redirect(url_for('users.view', id=user.id))
    
    return render_template('pages/users/create.html', roles=Role)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit user details."""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Check email uniqueness if changed
        if data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                flash('Email already registered', 'error')
                return redirect(url_for('users.edit', id=id))
        
        # Check username uniqueness if changed
        if data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                flash('Username already taken', 'error')
                return redirect(url_for('users.edit', id=id))
        
        # Update user fields
        user.email = data['email']
        user.username = data['username']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.phone = data.get('phone')
        user.address = data.get('address')
        user.city = data.get('city')
        user.state = data.get('state')
        user.zip_code = data.get('zip_code')
        
        # Update role if changed
        if data.get('role'):
            user.role = Role[data['role'].upper()]
        
        # Update status
        user.is_active = data.get('is_active') == 'on'
        user.is_verified = data.get('is_verified') == 'on'
        
        # Update password if provided
        if data.get('new_password'):
            user.set_password(data['new_password'])
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.view', id=id))
    
    return render_template('pages/users/edit.html', 
                         user=user,
                         roles=Role)


@bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(id):
    """Toggle user active status."""
    user = User.query.get_or_404(id)
    
    # Prevent deactivating yourself
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('users.view', id=id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {status} successfully!', 'success')
    return redirect(url_for('users.view', id=id))


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Delete a user (soft delete)."""
    user = User.query.get_or_404(id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('users.index'))
    
    # Check for active bookings
    active_bookings = Booking.query.filter_by(customer_id=user.id).filter(
        Booking.status.in_(['pending', 'confirmed', 'in_progress'])
    ).count()
    
    if active_bookings > 0:
        flash('Cannot delete user with active bookings.', 'error')
        return redirect(url_for('users.view', id=id))
    
    # Soft delete - just deactivate
    user.is_active = False
    db.session.commit()
    
    flash('User account deactivated.', 'info')
    return redirect(url_for('users.index'))


from flask_login import current_user