import os
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
from flask import current_app
from app import db
from app.models import Booking, DirectDebitSchedule, Payment, PaymentStatus, PaymentMethod
from app.utils.xero import XeroClient


class XeroInvoiceScheduler:
    """Service for scheduling and creating Xero invoices based on direct debit schedules."""
    
    def __init__(self):
        self.xero_client = XeroClient()
    
    def schedule_recurring_invoices(self, booking_id: int) -> bool:
        """
        Schedule recurring invoices based on direct debit schedule.
        This should be called after a successful handover with direct debit setup.
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False
        
        # Get the direct debit schedule
        schedule = DirectDebitSchedule.query.filter_by(booking_id=booking_id).first()
        if not schedule or not schedule.recurring_amount:
            return False
        
        # Store the schedule details for invoice generation
        # In a production system, you'd want to use a proper task scheduler like Celery
        # For now, we'll store the schedule details and check them periodically
        
        # Add a note to the booking
        schedule_note = f"\nDirect Debit Schedule created: {schedule.schedule_id}"
        if schedule.recurring_amount:
            schedule_note += f"\nRecurring: ${schedule.recurring_amount} {schedule.frequency}"
            schedule_note += f"\nStarting: {schedule.recurring_start_date}"
        
        if booking.admin_notes:
            booking.admin_notes += schedule_note
        else:
            booking.admin_notes = schedule_note
        
        db.session.commit()
        return True
    
    def create_scheduled_invoice(self, booking_id: int, amount: float, due_date: date, description: str = None) -> Optional[Dict[str, Any]]:
        """
        Create a Xero invoice for a scheduled payment.
        This should be called 1 day before the direct debit is due.
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
        
        try:
            # Prepare invoice data
            invoice_data = {
                'Type': 'ACCREC',  # Accounts Receivable
                'Contact': {
                    'Name': booking.customer.full_name,
                    'EmailAddress': booking.customer.email,
                    'Phones': [
                        {
                            'PhoneType': 'DEFAULT',
                            'PhoneNumber': booking.customer.phone or ''
                        }
                    ],
                    'Addresses': [
                        {
                            'AddressType': 'POBOX',
                            'AddressLine1': booking.customer.address or '',
                            'City': booking.customer.city or '',
                            'Region': booking.customer.state or '',
                            'PostalCode': booking.customer.zip_code or '',
                            'Country': booking.customer.country or 'Australia'
                        }
                    ]
                },
                'Date': datetime.utcnow().strftime('%Y-%m-%d'),
                'DueDate': due_date.strftime('%Y-%m-%d'),
                'Reference': booking.booking_number,
                'LineItems': [
                    {
                        'Description': description or f'Car Rental - {booking.car.full_name} - Booking {booking.booking_number}',
                        'Quantity': 1,
                        'UnitAmount': amount,
                        'AccountCode': os.getenv('XERO_SALES_ACCOUNT_CODE', '200'),  # Sales account
                        'TaxType': 'OUTPUT'  # GST on sales
                    }
                ],
                'Status': 'AUTHORISED'  # Create as authorized invoice
            }
            
            # Create invoice in Xero
            response = self.xero_client.create_invoice(invoice_data)
            
            if response and 'Invoices' in response and len(response['Invoices']) > 0:
                invoice = response['Invoices'][0]
                invoice_id = invoice.get('InvoiceID')
                invoice_number = invoice.get('InvoiceNumber')
                
                # Record the payment as pending
                payment = Payment(
                    booking_id=booking_id,
                    user_id=booking.customer_id,
                    amount=amount,
                    payment_method=PaymentMethod.DIRECT_DEBIT,
                    status=PaymentStatus.PENDING,
                    transaction_id=invoice_number,
                    payment_date=due_date,
                    notes=f"Scheduled invoice: {invoice_number}"
                )
                db.session.add(payment)
                
                # Add note to booking
                invoice_note = f"\nInvoice created: {invoice_number} for ${amount:.2f} due {due_date}"
                if booking.admin_notes:
                    booking.admin_notes += invoice_note
                else:
                    booking.admin_notes = invoice_note
                
                db.session.commit()
                
                # Send invoice to customer
                if invoice_id:
                    self.xero_client.send_invoice(invoice_id)
                
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'invoice_number': invoice_number
                }
            
        except Exception as e:
            print(f"Error creating scheduled invoice: {e}")
            return None
    
    def check_and_create_due_invoices(self):
        """
        Check all active direct debit schedules and create invoices for payments due tomorrow.
        This should be run daily as a scheduled job.
        """
        tomorrow = date.today() + timedelta(days=1)
        
        # Get all active schedules
        schedules = DirectDebitSchedule.query.filter_by(status='active').all()
        
        for schedule in schedules:
            # Check if an invoice needs to be created based on the schedule
            if self._should_create_invoice(schedule, tomorrow):
                # Calculate the invoice amount
                amount = schedule.recurring_amount
                
                # Create the invoice
                self.create_scheduled_invoice(
                    booking_id=schedule.booking_id,
                    amount=amount,
                    due_date=tomorrow,
                    description=f"{schedule.description} - Payment due {tomorrow.strftime('%Y-%m-%d')}"
                )
    
    def _should_create_invoice(self, schedule: DirectDebitSchedule, check_date: date) -> bool:
        """
        Determine if an invoice should be created for a given date based on the schedule.
        """
        if not schedule.recurring_start_date or not schedule.recurring_amount:
            return False
        
        # Check if the date is after the start date
        if check_date < schedule.recurring_start_date:
            return False
        
        # Calculate based on frequency
        days_since_start = (check_date - schedule.recurring_start_date).days
        
        if schedule.frequency == 'weekly':
            return days_since_start % 7 == 0
        elif schedule.frequency == 'fortnightly':
            return days_since_start % 14 == 0
        elif schedule.frequency == 'monthly':
            # Check if it's the same day of the month
            return check_date.day == schedule.recurring_start_date.day
        
        return False
    
    def cancel_scheduled_invoices(self, booking_id: int) -> bool:
        """
        Cancel all scheduled invoices for a booking.
        Called when a booking is cancelled or completed.
        """
        try:
            # Update the direct debit schedule status
            schedule = DirectDebitSchedule.query.filter_by(booking_id=booking_id).first()
            if schedule:
                schedule.status = 'cancelled'
                db.session.commit()
            
            return True
        except Exception as e:
            print(f"Error cancelling scheduled invoices: {e}")
            return False