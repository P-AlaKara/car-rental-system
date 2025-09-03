import base64
import json
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
from flask import current_app, url_for
from app import db
from app.models import XeroToken


class XeroClient:
    """Client for interacting with Xero API."""
    
    XERO_AUTH_URL = 'https://login.xero.com/identity/connect/authorize'
    XERO_TOKEN_URL = 'https://identity.xero.com/connect/token'
    XERO_CONNECTIONS_URL = 'https://api.xero.com/connections'
    XERO_API_URL = 'https://api.xero.com/api.xro/2.0'
    
    def __init__(self):
        self.client_id = current_app.config.get('XERO_CLIENT_ID')
        self.client_secret = current_app.config.get('XERO_CLIENT_SECRET')
        self.callback_url = current_app.config.get('XERO_CALLBACK_URL')
        self.scopes = current_app.config.get('XERO_SCOPES', [])
        
    def get_authorization_url(self, state=None):
        """Generate the Xero OAuth2 authorization URL."""
        if not state:
            state = secrets.token_urlsafe(32)
            
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'scope': ' '.join(self.scopes),
            'state': state
        }
        
        return f"{self.XERO_AUTH_URL}?{urlencode(params)}", state
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access and refresh tokens."""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': self._get_basic_auth_header()
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.callback_url
        }
        
        response = requests.post(self.XERO_TOKEN_URL, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token exchange failed: {response.text}")
    
    def refresh_access_token(self, refresh_token):
        """Refresh the access token using the refresh token."""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': self._get_basic_auth_header()
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = requests.post(self.XERO_TOKEN_URL, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token refresh failed: {response.text}")
    
    def get_tenant_connections(self, access_token):
        """Get list of tenant connections for the authenticated user."""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(self.XERO_CONNECTIONS_URL, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get connections: {response.text}")
    
    def get_valid_token(self):
        """Get a valid access token, refreshing if necessary."""
        # Get the latest token from database
        token = XeroToken.query.order_by(XeroToken.created_at.desc()).first()
        
        if not token:
            raise Exception("No Xero token found. Please authorize the application first.")
        
        # Check if token needs refresh
        if token.needs_refresh:
            try:
                # Refresh the token
                token_data = self.refresh_access_token(token.refresh_token)
                
                # Update the token in database
                token.update_tokens(token_data)
                db.session.commit()
                
                current_app.logger.info("Xero token refreshed successfully")
            except Exception as e:
                current_app.logger.error(f"Failed to refresh Xero token: {str(e)}")
                raise
        
        return token
    
    def create_invoice(self, booking_data, invoice_amount, due_date):
        """Create an invoice in Xero."""
        token = self.get_valid_token()
        
        if not token.tenant_id:
            raise Exception("No tenant ID found. Please reconnect to Xero.")
        
        # Prepare invoice data
        invoice = {
            "Type": "ACCREC",  # Accounts Receivable invoice
            "Contact": {
                "Name": booking_data.get('customer_name'),
                "EmailAddress": booking_data.get('customer_email'),
                "Phones": [
                    {
                        "PhoneType": "MOBILE",
                        "PhoneNumber": booking_data.get('customer_phone', '')
                    }
                ]
            },
            "Date": datetime.utcnow().strftime("%Y-%m-%d"),
            "DueDate": due_date.strftime("%Y-%m-%d") if isinstance(due_date, datetime) else due_date,
            "Reference": booking_data.get('booking_number'),
            "Status": "AUTHORISED",
            "LineAmountTypes": "Exclusive",  # Tax exclusive
            "LineItems": [
                {
                    "Description": self._generate_invoice_description(booking_data),
                    "Quantity": 1,
                    "UnitAmount": invoice_amount,
                    "AccountCode": "200",  # Sales account code - you may need to adjust this
                    "TaxType": "OUTPUT"  # Standard tax - adjust based on your Xero setup
                }
            ],
            "BrandingThemeID": None,  # You can set a specific branding theme ID if needed
        }
        
        headers = {
            'Authorization': f'Bearer {token.access_token}',
            'Xero-tenant-id': token.tenant_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            f"{self.XERO_API_URL}/Invoices",
            headers=headers,
            json={"Invoices": [invoice]}
        )
        
        if response.status_code in [200, 201]:
            invoice_data = response.json()
            return invoice_data.get('Invoices', [{}])[0]
        else:
            raise Exception(f"Failed to create invoice: {response.text}")
    
    def send_invoice(self, invoice_id):
        """Send an invoice to the customer via email."""
        token = self.get_valid_token()
        
        if not token.tenant_id:
            raise Exception("No tenant ID found. Please reconnect to Xero.")
        
        headers = {
            'Authorization': f'Bearer {token.access_token}',
            'Xero-tenant-id': token.tenant_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # First, get the invoice to ensure it exists and get the contact email
        invoice_response = requests.get(
            f"{self.XERO_API_URL}/Invoices/{invoice_id}",
            headers=headers
        )
        
        if invoice_response.status_code != 200:
            raise Exception(f"Failed to get invoice: {invoice_response.text}")
        
        invoice = invoice_response.json().get('Invoices', [{}])[0]
        
        # Send the invoice via email
        email_data = {
            "IncludeOnline": True  # Include online invoice link
        }
        
        response = requests.post(
            f"{self.XERO_API_URL}/Invoices/{invoice_id}/Email",
            headers=headers,
            json=email_data
        )
        
        if response.status_code in [200, 204]:
            return {
                'success': True,
                'message': 'Invoice sent successfully',
                'invoice_id': invoice_id,
                'invoice_number': invoice.get('InvoiceNumber')
            }
        else:
            raise Exception(f"Failed to send invoice: {response.text}")
    
    def create_and_send_invoice(self, booking_data, invoice_amount, due_date):
        """Create and send an invoice in one operation."""
        try:
            # Create the invoice
            invoice = self.create_invoice(booking_data, invoice_amount, due_date)
            
            if not invoice or not invoice.get('InvoiceID'):
                raise Exception("Failed to create invoice - no invoice ID returned")
            
            # Send the invoice
            result = self.send_invoice(invoice['InvoiceID'])
            
            # Add invoice details to result
            result['invoice'] = invoice
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Failed to create and send invoice: {str(e)}")
            raise
    
    def _generate_invoice_description(self, booking_data):
        """Generate a detailed invoice description from booking data."""
        lines = []
        
        # Basic booking info
        lines.append(f"Car Rental - Booking #{booking_data.get('booking_number', 'N/A')}")
        
        # Car details
        if booking_data.get('car_name'):
            lines.append(f"Vehicle: {booking_data['car_name']}")
        
        # Rental period
        if booking_data.get('pickup_date') and booking_data.get('return_date'):
            lines.append(f"Rental Period: {booking_data['pickup_date']} to {booking_data['return_date']}")
        
        # Locations
        if booking_data.get('pickup_location'):
            lines.append(f"Pickup Location: {booking_data['pickup_location']}")
        if booking_data.get('return_location'):
            lines.append(f"Return Location: {booking_data['return_location']}")
        
        # Additional services
        services = []
        if booking_data.get('with_driver'):
            services.append("Driver Service")
        if booking_data.get('insurance_opted'):
            services.append("Insurance")
        if booking_data.get('gps_opted'):
            services.append("GPS")
        if booking_data.get('child_seat_opted'):
            services.append("Child Seat")
        
        if services:
            lines.append(f"Additional Services: {', '.join(services)}")
        
        # Pricing breakdown
        if booking_data.get('daily_rate') and booking_data.get('total_days'):
            lines.append(f"Daily Rate: ${booking_data['daily_rate']:.2f} x {booking_data['total_days']} days")
        
        return '\n'.join(lines)
    
    def _get_basic_auth_header(self):
        """Generate Basic Auth header for client credentials."""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def disconnect(self):
        """Disconnect from Xero by removing stored tokens."""
        try:
            # Delete all stored tokens
            XeroToken.query.delete()
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to disconnect from Xero: {str(e)}")
            db.session.rollback()
            return False