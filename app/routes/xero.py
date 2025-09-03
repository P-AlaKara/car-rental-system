from flask import Blueprint, request, jsonify, session, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import XeroToken, Booking, User, Role
from app.utils.xero import XeroClient
import logging

logger = logging.getLogger(__name__)

xero_bp = Blueprint('xero', __name__, url_prefix='/xero')


@xero_bp.route('/authorize')
@login_required
def authorize():
    """Initiate Xero OAuth2 authorization flow."""
    # Check if user is admin
    if current_user.role != Role.ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        client = XeroClient()
        auth_url, state = client.get_authorization_url()
        
        # Store state in session for verification
        session['xero_oauth_state'] = state
        
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"Failed to initiate Xero authorization: {str(e)}")
        flash('Failed to connect to Xero. Please check your configuration.', 'error')
        return redirect(url_for('admin.settings'))


@xero_bp.route('/callback')
@login_required
def callback():
    """Handle Xero OAuth2 callback."""
    # Check if user is admin
    if current_user.role != Role.ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Verify state
    state = request.args.get('state')
    if not state or state != session.get('xero_oauth_state'):
        flash('Invalid state parameter. Please try again.', 'error')
        return redirect(url_for('admin.settings'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        error = request.args.get('error', 'Unknown error')
        flash(f'Authorization failed: {error}', 'error')
        return redirect(url_for('admin.settings'))
    
    try:
        client = XeroClient()
        
        # Exchange code for tokens
        token_data = client.exchange_code_for_token(code)
        
        # Get tenant connections
        connections = client.get_tenant_connections(token_data['access_token'])
        
        if not connections:
            flash('No Xero organizations found. Please connect an organization.', 'error')
            return redirect(url_for('admin.settings'))
        
        # Use the first tenant (you might want to let user choose if multiple)
        tenant = connections[0]
        
        # Check if we already have a token stored
        existing_token = XeroToken.query.first()
        
        if existing_token:
            # Update existing token
            existing_token.update_tokens(token_data)
            existing_token.tenant_id = tenant['tenantId']
            existing_token.tenant_name = tenant.get('tenantName', '')
            existing_token.tenant_type = tenant.get('tenantType', '')
        else:
            # Create new token record
            new_token = XeroToken()
            new_token.update_tokens(token_data)
            new_token.tenant_id = tenant['tenantId']
            new_token.tenant_name = tenant.get('tenantName', '')
            new_token.tenant_type = tenant.get('tenantType', '')
            db.session.add(new_token)
        
        db.session.commit()
        
        # Clean up session
        session.pop('xero_oauth_state', None)
        
        flash(f'Successfully connected to Xero organization: {tenant.get("tenantName", "Unknown")}', 'success')
        return redirect(url_for('admin.settings'))
        
    except Exception as e:
        logger.error(f"Failed to complete Xero authorization: {str(e)}")
        flash('Failed to complete authorization. Please try again.', 'error')
        return redirect(url_for('admin.settings'))


@xero_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect from Xero."""
    # Check if user is admin
    if current_user.role != Role.ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        client = XeroClient()
        if client.disconnect():
            return jsonify({
                'success': True,
                'message': 'Successfully disconnected from Xero'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to disconnect from Xero'
            }), 500
            
    except Exception as e:
        logger.error(f"Failed to disconnect from Xero: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@xero_bp.route('/status')
@login_required
def status():
    """Check Xero connection status."""
    # Check if user is admin
    if current_user.role != Role.ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        token = XeroToken.query.order_by(XeroToken.created_at.desc()).first()
        
        if not token:
            return jsonify({
                'connected': False,
                'message': 'Not connected to Xero'
            })
        
        return jsonify({
            'connected': True,
            'tenant_name': token.tenant_name,
            'tenant_id': token.tenant_id,
            'expires_at': token.expires_at.isoformat() if token.expires_at else None,
            'is_expired': token.is_expired,
            'needs_refresh': token.needs_refresh
        })
        
    except Exception as e:
        logger.error(f"Failed to check Xero status: {str(e)}")
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 500


@xero_bp.route('/send-invoice', methods=['POST'])
@login_required
def send_invoice():
    """Send an invoice for a booking."""
    try:
        data = request.get_json()
        
        # Validate required fields
        booking_id = data.get('booking_id')
        invoice_amount = data.get('invoice_amount')
        due_date = data.get('due_date')
        
        if not all([booking_id, invoice_amount, due_date]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields: booking_id, invoice_amount, due_date'
            }), 400
        
        # Get booking details
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({
                'success': False,
                'message': 'Booking not found'
            }), 404
        
        # Get customer details
        customer = User.query.get(booking.customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Prepare booking data for invoice
        booking_data = {
            'booking_number': booking.booking_number,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'customer_email': customer.email,
            'customer_phone': customer.phone,
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
        
        # Parse due date
        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
        
        # Create and send invoice
        client = XeroClient()
        result = client.create_and_send_invoice(
            booking_data=booking_data,
            invoice_amount=float(invoice_amount),
            due_date=due_date
        )
        
        # Store invoice reference in booking (you might want to add an invoice_id field to Booking model)
        if result.get('invoice'):
            booking.admin_notes = (booking.admin_notes or '') + f"\nXero Invoice: {result['invoice'].get('InvoiceNumber')} (ID: {result['invoice'].get('InvoiceID')})"
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invoice sent successfully',
            'invoice_number': result.get('invoice', {}).get('InvoiceNumber'),
            'invoice_id': result.get('invoice', {}).get('InvoiceID')
        })
        
    except Exception as e:
        logger.error(f"Failed to send invoice: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@xero_bp.route('/test-connection', methods=['GET'])
@login_required
def test_connection():
    """Test the Xero connection by fetching organization details."""
    # Check if user is admin
    if current_user.role != Role.ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        client = XeroClient()
        token = client.get_valid_token()
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'No Xero connection found'
            }), 404
        
        # Try to get organization details
        headers = {
            'Authorization': f'Bearer {token.access_token}',
            'Xero-tenant-id': token.tenant_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        import requests
        response = requests.get(
            f"{client.XERO_API_URL}/Organisation",
            headers=headers
        )
        
        if response.status_code == 200:
            org_data = response.json()
            return jsonify({
                'success': True,
                'message': 'Connection successful',
                'organization': org_data.get('Organisations', [{}])[0]
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Connection test failed: {response.text}'
            }), 500
            
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500