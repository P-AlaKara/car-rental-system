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
    """Pay Advantage arming-compatible webhook endpoint.

    Returns the exact HTTP status codes required by Pay Advantage's arming tests.
    """
    try:
        raw_body = request.get_data() or b''

        # 403: missing or empty signature header
        signature = request.headers.get('x-payadvantage-signature') or request.headers.get('X-PayAdvantage-Signature')
        if signature is None or signature.strip() == "":
            return "", 403

        # 401: signature mismatch
        secret = current_app.config.get('PAY_ADVANTAGE_WEBHOOK_SECRET') or ""
        digest_hex = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
        provided = signature.strip()
        if provided.lower().startswith('sha256='):
            provided = provided.split('=', 1)[1].strip()
        # Compare as lowercase hex
        if not hmac.compare_digest(provided.lower(), digest_hex):
            return "", 401

        # 400: invalid JSON, not an array, or empty array
        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except Exception:
            return "", 400
        if not isinstance(payload, list) or len(payload) == 0:
            return "", 400

        # 400: missing required fields or any required field null/empty
        required_fields = {"Code", "DateCreated", "Event", "Status", "ResourceUrl"}
        for item in payload:
            if not isinstance(item, dict):
                return "", 400
            if not required_fields.issubset(item.keys()):
                return "", 400
            for field in required_fields:
                value = item.get(field)
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    return "", 400

        # 202: success, acknowledge quickly; process asynchronously elsewhere
        return "", 202
    except Exception as e:
        current_app.logger.error(f"PayAdvantage webhook error: {e}")
        # Fallback to 400 on unexpected errors to avoid 5xx during arming
        return "", 400


@webhooks_bp.route('/payadvantage/health')
def payadvantage_webhook_health():
    return jsonify({'status': 'ok'})

