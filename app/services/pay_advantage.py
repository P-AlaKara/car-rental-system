import os
import requests
from datetime import datetime, date
from typing import Dict, Optional, Any
from app import db
from app.models import PayAdvantageCustomer, DirectDebitSchedule, User


class PayAdvantageService:
    """Service for interacting with PayAdvantage API."""
    
    def __init__(self):
        self.base_url = os.getenv('PAY_ADVANTAGE_API_URL', 'https://api.payadvantage.com.au')
        self.username = os.getenv('PAY_ADVANTAGE_USERNAME')
        self.password = os.getenv('PAY_ADVANTAGE_PASSWORD')
        self.token = None
        self.token_expiry = None
    
    def _get_token(self) -> str:
        """Get or refresh authentication token."""
        if self.token and self.token_expiry and datetime.utcnow() < self.token_expiry:
            return self.token
        
        # Exchange username/password for token
        response = requests.post(
            f"{self.base_url}/v3/authenticate",
            json={
                "username": self.username,
                "password": self.password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
            # Assume token expires in 1 hour (adjust based on actual API)
            from datetime import timedelta
            self.token_expiry = datetime.utcnow() + timedelta(hours=1)
            return self.token
        else:
            raise Exception(f"Failed to authenticate with PayAdvantage: {response.text}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to PayAdvantage API."""
        token = self._get_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=data)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"PayAdvantage API error: {response.status_code} - {response.text}")
    
    def get_or_create_customer(self, user: User) -> PayAdvantageCustomer:
        """Get existing or create new PayAdvantage customer."""
        # Check if customer already exists in our database
        pa_customer = PayAdvantageCustomer.query.filter_by(user_id=user.id).first()
        
        if pa_customer:
            # Verify customer still exists in PayAdvantage
            try:
                self._make_request('GET', f'/v3/customers/{pa_customer.customer_code}')
                return pa_customer
            except:
                # Customer doesn't exist in PayAdvantage, remove from our DB
                db.session.delete(pa_customer)
                db.session.commit()
        
        # Create new customer in PayAdvantage
        customer_data = {
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "phone": user.phone or "",
            "address": {
                "line1": user.address or "",
                "city": user.city or "",
                "state": user.state or "",
                "postcode": user.zip_code or "",
                "country": user.country or "Australia"
            }
        }
        
        response = self._make_request('POST', '/v3/customers', customer_data)
        customer_code = response.get('customerCode')
        
        # Save customer code to database
        pa_customer = PayAdvantageCustomer(
            user_id=user.id,
            customer_code=customer_code
        )
        db.session.add(pa_customer)
        db.session.commit()
        
        return pa_customer
    
    def create_direct_debit_schedule(
        self,
        booking_id: int,
        customer_code: str,
        description: str,
        upfront_amount: Optional[float] = None,
        upfront_date: Optional[date] = None,
        recurring_amount: Optional[float] = None,
        recurring_start_date: Optional[date] = None,
        frequency: Optional[str] = None,  # weekly, fortnightly, monthly
        end_condition_amount: Optional[float] = None,
        reminder_days: int = 2
    ) -> Dict[str, Any]:
        """Create a direct debit schedule and get authorization URL."""
        
        # Build the schedule data
        schedule_data = {
            "customer": {
                "customerCode": customer_code
            },
            "description": description,
            "reminderDays": reminder_days,
            "onChargedFees": {
                "feeType": "percentage",  # or "fixed"
                "feeAmount": 0  # Default to no fees, can be configured
            }
        }
        
        # Add upfront payment if provided
        if upfront_amount and upfront_date:
            schedule_data["upfrontPayment"] = {
                "amount": upfront_amount,
                "date": upfront_date.isoformat()
            }
        
        # Add recurring payment if provided
        if recurring_amount and recurring_start_date and frequency:
            schedule_data["recurringPayment"] = {
                "amount": recurring_amount,
                "startDate": recurring_start_date.isoformat(),
                "frequency": frequency
            }
            
            # Add end condition if provided
            if end_condition_amount:
                schedule_data["recurringPayment"]["endCondition"] = {
                    "type": "totalAmount",
                    "value": end_condition_amount
                }
        
        # Create the schedule
        response = self._make_request('POST', '/v3/directdebits/schedules', schedule_data)
        
        schedule_id = response.get('scheduleId')
        authorization_url = response.get('authorizationUrl')
        
        # Save schedule to database
        schedule = DirectDebitSchedule(
            booking_id=booking_id,
            schedule_id=schedule_id,
            description=description,
            upfront_amount=upfront_amount,
            upfront_date=upfront_date,
            recurring_amount=recurring_amount,
            recurring_start_date=recurring_start_date,
            frequency=frequency,
            end_condition_amount=end_condition_amount,
            status='pending_authorization',
            authorization_url=authorization_url
        )
        db.session.add(schedule)
        db.session.commit()
        
        return {
            'schedule_id': schedule_id,
            'authorization_url': authorization_url,
            'schedule': schedule
        }
    
    def get_schedule_status(self, schedule_id: str) -> Dict[str, Any]:
        """Get the status of a direct debit schedule."""
        response = self._make_request('GET', f'/v3/directdebits/schedules/{schedule_id}')
        return response
    
    def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancel a direct debit schedule."""
        try:
            self._make_request('DELETE', f'/v3/directdebits/schedules/{schedule_id}')
            
            # Update local database
            schedule = DirectDebitSchedule.query.filter_by(schedule_id=schedule_id).first()
            if schedule:
                schedule.status = 'cancelled'
                db.session.commit()
            
            return True
        except Exception as e:
            print(f"Error cancelling schedule: {e}")
            return False