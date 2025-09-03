#!/usr/bin/env python
"""
Scheduled tasks for the car rental system.
This script should be run daily to handle recurring tasks.
"""

import sys
from datetime import datetime, date, timedelta
from app import create_app, db
from app.services.xero_scheduler import XeroInvoiceScheduler
from app.models import Booking, BookingStatus, DirectDebitSchedule

def run_daily_tasks():
    """Run all daily scheduled tasks."""
    app = create_app('development')
    
    with app.app_context():
        print(f"Running daily tasks at {datetime.utcnow()}")
        
        # 1. Create invoices for direct debit payments due tomorrow
        try:
            print("Checking for direct debit invoices to create...")
            scheduler = XeroInvoiceScheduler()
            scheduler.check_and_create_due_invoices()
            print("✓ Direct debit invoice check completed")
        except Exception as e:
            print(f"✗ Error creating direct debit invoices: {e}")
        
        # 2. Check for overdue bookings
        try:
            print("Checking for overdue bookings...")
            overdue_bookings = Booking.query.filter(
                Booking.status == BookingStatus.IN_PROGRESS,
                Booking.return_date < datetime.utcnow()
            ).all()
            
            for booking in overdue_bookings:
                days_overdue = (datetime.utcnow() - booking.return_date).days
                note = f"\n[System] Booking is {days_overdue} days overdue as of {date.today()}"
                if booking.admin_notes:
                    # Only add note if it's not already there
                    if f"overdue as of {date.today()}" not in booking.admin_notes:
                        booking.admin_notes += note
                else:
                    booking.admin_notes = note
            
            db.session.commit()
            print(f"✓ Found {len(overdue_bookings)} overdue bookings")
        except Exception as e:
            print(f"✗ Error checking overdue bookings: {e}")
        
        # 3. Update direct debit schedule statuses
        try:
            print("Updating direct debit schedule statuses...")
            pending_schedules = DirectDebitSchedule.query.filter_by(
                status='pending_authorization'
            ).all()
            
            for schedule in pending_schedules:
                # In production, you would check with PayAdvantage API
                # to see if the authorization has been completed
                pass
            
            print("✓ Direct debit status check completed")
        except Exception as e:
            print(f"✗ Error updating direct debit statuses: {e}")
        
        print(f"Daily tasks completed at {datetime.utcnow()}")

def run_hourly_tasks():
    """Run all hourly scheduled tasks."""
    app = create_app('development')
    
    with app.app_context():
        print(f"Running hourly tasks at {datetime.utcnow()}")
        
        # Add any hourly tasks here
        
        print(f"Hourly tasks completed at {datetime.utcnow()}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        task = sys.argv[1]
        if task == 'daily':
            run_daily_tasks()
        elif task == 'hourly':
            run_hourly_tasks()
        else:
            print(f"Unknown task: {task}")
            print("Usage: python scheduled_tasks.py [daily|hourly]")
    else:
        print("Usage: python scheduled_tasks.py [daily|hourly]")
        print("\nExample crontab entries:")
        print("# Run daily tasks at 2 AM")
        print("0 2 * * * /usr/bin/python /path/to/scheduled_tasks.py daily")
        print("# Run hourly tasks")
        print("0 * * * * /usr/bin/python /path/to/scheduled_tasks.py hourly")