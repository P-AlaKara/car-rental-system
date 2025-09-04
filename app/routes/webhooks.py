from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Payment, PaymentStatus, PaymentMethod, Booking
from datetime import datetime

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')


@webhooks_bp.route('/payadvantage', methods=['POST'])
def payadvantage_webhook():
    """Webhook receiver for Pay Advantage payment events.

    This endpoint upserts installments and, when payments complete, creates Payment records.
    """
    try:
        payload = request.get_json(silent=True) or {}

        # Normalize into a list of events if necessary
        events = payload if isinstance(payload, list) else [payload]

        from app.services.pay_advantage import PayAdvantageService
        pa_service = PayAdvantageService()

        processed = []
        for event in events:
            installment = pa_service.upsert_installment_from_webhook(event)

            # If completed, ensure a Payment record exists
            if installment and installment.status == 'completed':
                existing = None
                if installment.external_payment_id:
                    existing = Payment.query.filter_by(
                        gateway='payadvantage',
                        gateway_transaction_id=installment.external_payment_id,
                        booking_id=installment.booking_id
                    ).first()

                if not existing:
                    # Create payment
                    booking = Booking.query.get(installment.booking_id)
                    if not booking:
                        # Skip if booking missing
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
                        gateway_transaction_id=installment.external_payment_id,
                        gateway_response=event,
                        description=f'Direct debit payment for booking {booking.booking_number}',
                        processed_at=datetime.utcnow()
                    )
                    payment.generate_transaction_id()
                    db.session.add(payment)
                    db.session.commit()

            processed.append({
                'installment_id': installment.id if installment else None,
                'booking_id': installment.booking_id if installment else None,
                'status': installment.status if installment else None
            })

        return jsonify({'success': True, 'processed': processed}), 200
    except Exception as e:
        current_app.logger.error(f"PayAdvantage webhook error: {e}")
        return jsonify({'success': False}), 400


@webhooks_bp.route('/payadvantage/health')
def payadvantage_webhook_health():
    return jsonify({'status': 'ok'})

