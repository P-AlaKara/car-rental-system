from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Payment, PaymentStatus, PaymentMethod, Booking
from datetime import datetime
import hmac
import hashlib
import json

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')


@webhooks_bp.route('/payadvantage', methods=['POST'])
def payadvantage_webhook():
    """Webhook receiver for Pay Advantage payment events.

    This endpoint verifies the signature (if configured), upserts installments,
    and when payments complete, creates idempotent Payment records and updates
    the associated Booking status.
    """
    try:
        # Verify signature if secret is configured
        secret = current_app.config.get('PAY_ADVANTAGE_WEBHOOK_SECRET')
        raw_body = request.get_data() or b''
        if secret:
            provided_sig = request.headers.get('X-PayAdvantage-Signature') or request.headers.get('X-PayAdvantage-Signature-SHA256')
            if not provided_sig:
                return jsonify({'success': False, 'error': 'missing_signature'}), 401
            digest = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
            # Accept either raw hex or prefixed format like 'sha256=hex'
            valid_sigs = {digest, f"sha256={digest}"}
            if provided_sig not in valid_sigs:
                return jsonify({'success': False, 'error': 'invalid_signature'}), 401

        # Parse JSON payload explicitly to avoid signature issues
        try:
            payload = json.loads(raw_body.decode('utf-8') or '{}')
        except Exception:
            return jsonify({'success': False, 'error': 'invalid_json'}), 400

        # Normalize into a list of events if necessary
        events = payload if isinstance(payload, list) else [payload]

        from app.services.pay_advantage import PayAdvantageService
        from app.models.booking import BookingStatus
        pa_service = PayAdvantageService()

        processed = []
        for event in events:
            if not isinstance(event, dict):
                processed.append({'error': 'invalid_event'})
                continue

            # Basic payload validation (must include scheduleId or paymentId)
            if not any(k in event for k in ['scheduleId', 'ScheduleId', 'paymentId', 'PaymentId', 'id']):
                processed.append({'error': 'missing_identifiers'})
                continue

            installment = pa_service.upsert_installment_from_webhook(event)

            # If completed, ensure a Payment record exists (idempotent)
            if installment and str(getattr(installment, 'status', '')).lower() == 'completed':
                # Build deterministic gateway transaction id for idempotency
                fallback_key = None
                try:
                    fallback_key = f"sched:{installment.schedule_id}|due:{installment.due_date.isoformat()}"
                except Exception:
                    fallback_key = None
                gateway_txn_id = installment.external_payment_id or fallback_key

                existing = None
                if gateway_txn_id:
                    existing = Payment.query.filter_by(
                        gateway='payadvantage',
                        gateway_transaction_id=gateway_txn_id,
                        booking_id=installment.booking_id
                    ).first()

                if not existing:
                    # Create payment
                    booking = Booking.query.get(installment.booking_id)
                    if not booking:
                        # Skip if booking missing
                        processed.append({'error': 'booking_not_found'})
                        continue

                    amount = installment.paid_amount or installment.due_amount or 0

                    payment = Payment(
                        booking_id=booking.id,
                        user_id=booking.customer_id,
                        amount=amount,
                        currency='AUD',
                        payment_method=PaymentMethod.DIRECT_DEBIT,
                        status=PaymentStatus.COMPLETED,
                        gateway='payadvantage',
                        gateway_transaction_id=gateway_txn_id,
                        gateway_response=event,
                        description=f'Direct debit payment for booking {booking.booking_number}',
                        processed_at=datetime.utcnow()
                    )
                    payment.generate_transaction_id()
                    db.session.add(payment)

                    # Update booking status to confirmed if not already progressed
                    if booking.status in [BookingStatus.PENDING, BookingStatus.CANCELLED, BookingStatus.NO_SHOW]:
                        booking.status = BookingStatus.CONFIRMED

                    db.session.commit()

            processed.append({
                'installment_id': getattr(installment, 'id', None),
                'booking_id': getattr(installment, 'booking_id', None),
                'status': getattr(installment, 'status', None)
            })

        return jsonify({'success': True, 'processed': processed}), 200
    except Exception as e:
        current_app.logger.error(f"PayAdvantage webhook error: {e}")
        return jsonify({'success': False}), 400


@webhooks_bp.route('/payadvantage/health')
def payadvantage_webhook_health():
    return jsonify({'status': 'ok'})

