# Invoice Sending Fix Summary

## Issues Identified and Fixed

### Issue 1: "Failed to send invoice" error despite 200 response
**Problem:** The send invoice form was showing "Failed to send invoice" even when the invoice was successfully sent (200 response, email received, invoice in Xero).

**Root Cause:** 
- The frontend JavaScript in `/templates/admin/send_invoice.html` was NOT sending the invoice_amount and due_date in the request body
- It was making a POST request with an empty body, causing the backend to potentially return unexpected results

**Fix Applied:**
```javascript
// Before (missing request body):
const response = await fetch(`/admin/api/booking/${bookingId}/send-invoice`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    }
});

// After (includes request body):
const invoiceAmount = document.getElementById('invoiceAmount').value;
const dueDate = document.getElementById('dueDate').value;

const response = await fetch(`/admin/api/booking/${bookingId}/send-invoice`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        invoice_amount: invoiceAmount,
        due_date: dueDate
    })
});
```

### Issue 2: Custom amount ignored (always sends full rental amount)
**Problem:** The custom invoice amount entered in the form was being ignored, and the system always sent the full booking.total_amount.

**Root Cause:** 
- The backend endpoint `/admin/api/booking/<id>/send-invoice` in `app/routes/admin.py` was hardcoded to use `booking.total_amount`
- It wasn't reading the custom invoice_amount from the request

**Fix Applied:**
```python
# Before (always uses booking total):
result = client.create_and_send_invoice(
    booking_data=booking_data,
    invoice_amount=float(booking.total_amount),  # Always uses booking total
    due_date=due_date
)

# After (uses custom amount if provided):
data = request.get_json() or {}
custom_invoice_amount = data.get('invoice_amount')
custom_due_date = data.get('due_date')

# Use custom invoice amount if provided, otherwise use booking total
invoice_amount = float(custom_invoice_amount) if custom_invoice_amount else float(booking.total_amount)

result = client.create_and_send_invoice(
    booking_data=booking_data,
    invoice_amount=invoice_amount,  # Now uses custom amount
    due_date=due_date
)
```

## Additional Improvements

### 1. Better Error Handling
Added improved error logging and response checking:
```javascript
// Now checks both response.ok and result.success
if (response.ok && result.success) {
    // Success handling
    console.log('Invoice sent successfully:', result);
} else {
    // Better error logging
    console.error('Failed to send invoice:', errorMsg, 'Response status:', response.status, 'Result:', result);
}
```

### 2. Custom Due Date Support
The backend now also accepts and uses custom due dates from the frontend:
```python
if custom_due_date:
    try:
        due_date = datetime.strptime(custom_due_date, '%Y-%m-%d')
    except:
        due_date = datetime.utcnow() + timedelta(days=7)
else:
    due_date = datetime.utcnow() + timedelta(days=7)
```

## Files Modified

1. **`/templates/admin/send_invoice.html`**
   - Added code to send invoice_amount and due_date in request body
   - Improved error handling and logging
   - Better response status checking

2. **`/app/routes/admin.py`**
   - Modified `send_invoice()` function to accept custom invoice_amount from request
   - Added support for custom due_date from request
   - Uses custom amount if provided, otherwise falls back to booking total

## Testing

A test script has been created at `/workspace/test_invoice_fix.py` to verify the fixes:
```bash
python test_invoice_fix.py
```

This script tests:
- Custom invoice amount submission
- Custom due date submission
- Both the admin endpoint and direct Xero endpoint
- Proper error handling

## How It Works Now

1. **Custom Invoice Form** (`/admin/booking/<id>/send-invoice`):
   - User enters custom invoice amount and due date
   - JavaScript properly sends these values in the request body
   - Backend uses the custom amount instead of the booking total
   - Invoice is created in Xero with the custom amount
   - Success/error messages are displayed correctly

2. **Quick Send Invoice** (from bookings list):
   - This already worked correctly as it was using the `/xero/send-invoice` endpoint
   - That endpoint properly accepts custom amounts

## Verification Steps

1. Go to Admin → Bookings
2. Click on "Send invoice with details" (dollar icon) for any booking
3. Enter a custom invoice amount (different from the total)
4. Set a due date
5. Click "Send Invoice"
6. Verify:
   - Success message appears (not error)
   - Invoice in Xero shows the custom amount
   - Email received shows the custom amount
   - Console logs show successful response

## Notes

- The fix maintains backward compatibility - if no custom amount is provided, it uses the booking total
- Both endpoints (`/admin/api/booking/<id>/send-invoice` and `/xero/send-invoice`) now work consistently
- Error messages are more informative for debugging