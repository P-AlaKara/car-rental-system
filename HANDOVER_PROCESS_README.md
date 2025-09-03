# Vehicle Handover Process Implementation

## Overview
The vehicle handover process has been fully implemented to streamline the rental vehicle pickup workflow. This feature enables administrators to complete all necessary steps when handing over a vehicle to a customer.

## Features Implemented

### 1. Driver License Verification
- Displays customer's driver license details from the system
- Checkbox confirmation that physical license matches system records
- Timestamp recording when verification is completed

### 2. Contract Management
- Placeholder for contract generation (template-based system ready for implementation)
- Upload functionality for signed contracts
- Storage of contract URLs in the database

### 3. Vehicle Condition Documentation
- Photo upload interface for capturing vehicle condition at pickup
- Support for multiple photos (front, back, sides, interior)
- Photos stored with booking reference for comparison during return
- Base64 image handling with server-side storage

### 4. Odometer Reading
- Input field for recording current odometer reading at pickup
- Stored for calculating actual usage during return

### 5. Direct Debit Setup (PayAdvantage Integration)
- Complete integration with PayAdvantage API
- Customer management:
  - Automatic creation of PayAdvantage customers
  - Reuse of existing customer codes
  - Customer data synchronization
- Direct debit schedule configuration:
  - Upfront payment (deposit)
  - Recurring payments (daily/weekly/fortnightly/monthly)
  - End condition based on total amount
  - Automatic reminder setup (2 days before payment)
- Authorization URL generation for customer consent
- Schedule tracking in database

### 6. Xero Invoice Automation
- Automatic invoice creation based on direct debit schedule
- Invoices generated 1 day before payment due date
- Invoice details include:
  - Customer information
  - Booking reference
  - Payment amount and due date
  - GST calculation
- Automatic invoice sending to customer email
- Payment tracking and status updates

## Database Changes

### New Tables
1. **booking_photos**
   - Stores vehicle condition photos
   - Links photos to bookings and upload users
   - Tracks photo type (pickup/return)

2. **pay_advantage_customers**
   - Maps users to PayAdvantage customer codes
   - Prevents duplicate customer creation

3. **direct_debit_schedules**
   - Stores direct debit configuration
   - Tracks schedule status and authorization
   - Links to bookings

### Updated Tables
- **bookings** table enhanced with:
  - License verification fields
  - Contract storage fields
  - Odometer readings (pickup/return)
  - Handover completion tracking
  - Direct debit schedule reference

## Configuration Required

### Environment Variables (.env)
```env
# PayAdvantage Configuration
PAY_ADVANTAGE_API_URL=https://api.payadvantage.com.au
PAY_ADVANTAGE_USERNAME=your-username
PAY_ADVANTAGE_PASSWORD=your-password

# Xero Configuration (existing)
XERO_CLIENT_ID=your-client-id
XERO_CLIENT_SECRET=your-client-secret
XERO_SALES_ACCOUNT_CODE=200

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

## Setup Instructions

1. **Run Database Migrations**
   ```bash
   python run_migrations.py
   ```
   This will:
   - Create new tables
   - Add new columns to existing tables
   - Create upload directories

2. **Configure PayAdvantage**
   - Add your PayAdvantage credentials to .env
   - Ensure API access is enabled in your PayAdvantage account

3. **Set Up Scheduled Tasks**
   - Add cron job for daily invoice generation:
   ```bash
   0 2 * * * /usr/bin/python /path/to/scheduled_tasks.py daily
   ```

## Usage

### Processing a Vehicle Handover

1. Navigate to Admin > Bookings
2. Find the confirmed booking
3. Click the key icon (Process vehicle handover)
4. Complete the 5-step process:
   - Verify driver license
   - Generate/upload contract (placeholder)
   - Upload vehicle photos
   - Record odometer reading
   - Set up direct debit schedule
5. Click "Complete Handover"

### Direct Debit Authorization
- After handover completion, if direct debit is configured:
  - System generates authorization URL
  - Admin can send URL to customer or open for in-person authorization
  - Customer completes authorization on PayAdvantage portal
  - Payments process automatically per schedule

### Invoice Generation
- Invoices are automatically created 1 day before each payment
- Run daily scheduled task to process due invoices
- Invoices are sent directly to customer email via Xero

## API Endpoints

### Handover Management
- `GET /admin/api/booking/<id>/handover-details` - Get booking details for handover
- `POST /admin/api/booking/<id>/complete-handover` - Complete handover process

### File Uploads
- `GET /uploads/<path:filename>` - Serve uploaded files (photos, contracts)

## Security Considerations

1. **Authentication**: All handover endpoints require admin authentication
2. **File Uploads**: 
   - Limited to image formats for photos
   - Max file size enforced (16MB default)
   - Files stored outside web root
3. **PayAdvantage**: 
   - Token-based authentication
   - Tokens refreshed automatically
   - Sensitive data not logged
4. **Data Validation**: All inputs validated before processing

## Future Enhancements

1. **Contract Generation**
   - Template-based contract generation
   - Dynamic field population from booking data
   - Digital signature integration

2. **Photo Analysis**
   - AI-based damage detection
   - Automatic comparison between pickup/return photos
   - Damage report generation

3. **Payment Reconciliation**
   - Automatic matching of PayAdvantage payments with Xero invoices
   - Failed payment handling and retry logic
   - Payment receipt generation

4. **Mobile App Integration**
   - Mobile interface for field staff
   - Offline photo capture with sync
   - Digital signature on mobile devices

## Troubleshooting

### Common Issues

1. **PayAdvantage Authentication Fails**
   - Check credentials in .env
   - Verify API access is enabled
   - Check network connectivity

2. **Photos Not Uploading**
   - Verify upload directory exists and is writable
   - Check file size limits
   - Ensure correct file formats

3. **Invoices Not Creating**
   - Verify Xero integration is configured
   - Check scheduled task is running
   - Review error logs for API issues

### Logs
- Handover errors logged to application logs
- PayAdvantage API errors printed to console
- Scheduled task outputs logged with timestamps

## Support
For issues or questions about the handover process, please check:
1. Application logs in the logs directory
2. Scheduled task output
3. PayAdvantage and Xero API documentation