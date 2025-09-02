import os
import json
import base64
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests
from flask import Flask, send_from_directory, request, redirect, jsonify


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(APP_ROOT, 'dist')
DATA_DIR = os.path.join(APP_ROOT, '.data')
DATA_FILE = os.path.join(DATA_DIR, 'xero.json')


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def read_saved_tokens() -> dict | None:
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def write_saved_tokens(payload: dict) -> None:
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)


def get_env(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    return val if val is not None else default


def get_oauth_config() -> dict:
    client_id = get_env('XERO_CLIENT_ID')
    client_secret = get_env('XERO_CLIENT_SECRET')
    redirect_uri = get_env('XERO_REDIRECT_URI', 'http://localhost:5173/api/xero-callback')
    if not client_id or not client_secret:
        raise RuntimeError('Missing Xero client credentials')
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'scopes': 'offline_access accounting.transactions accounting.contacts accounting.settings email',
        'authorize_url': 'https://login.xero.com/identity/connect/authorize',
        'token_url': 'https://identity.xero.com/connect/token',
        'connections_url': 'https://api.xero.com/connections',
        'api_base': 'https://api.xero.com/api.xro/2.0',
    }


def build_basic_auth_header(client_id: str, client_secret: str) -> str:
    token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    return f"Basic {token}"


def refresh_token_if_needed(tokens: dict, oauth: dict) -> dict:
    # If expires_at exists and is in the past or close, refresh using refresh_token
    expires_at = tokens.get('expires_at')
    if expires_at is not None:
        try:
            # expires_at is seconds since epoch
            if datetime.now(timezone.utc).timestamp() < float(expires_at) - 60:
                return tokens
        except Exception:
            pass

    refresh_token = tokens.get('refresh_token')
    if not refresh_token:
        return tokens

    headers = {
        'Authorization': build_basic_auth_header(oauth['client_id'], oauth['client_secret']),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    resp = requests.post(oauth['token_url'], headers=headers, data=data, timeout=30)
    resp.raise_for_status()
    token_set = resp.json()
    # Compute absolute expiry timestamp
    expires_in = token_set.get('expires_in')
    expires_at = None
    if isinstance(expires_in, (int, float)):
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=float(expires_in))).timestamp()

    tokens_updated = {
        'tokenSet': token_set,
        'tenantId': tokens.get('tenantId'),
        'updatedAt': datetime.now(timezone.utc).isoformat(),
        'expires_at': expires_at,
    }
    write_saved_tokens(tokens_updated)
    return tokens_updated


def authorized_headers(token: str, tenant_id: str | None = None) -> dict:
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    if tenant_id:
        headers['xero-tenant-id'] = tenant_id
    return headers


app = Flask(__name__, static_folder=DIST_DIR, static_url_path='')


@app.get('/api/xero-start')
def xero_start():
    try:
        oauth = get_oauth_config()
        params = {
            'response_type': 'code',
            'client_id': oauth['client_id'],
            'redirect_uri': oauth['redirect_uri'],
            'scope': oauth['scopes'],
        }
        url = f"{oauth['authorize_url']}?{urlencode(params)}"
        return redirect(url, code=302)
    except Exception as e:
        return jsonify({ 'message': 'Failed to start Xero OAuth', 'error': str(e) }), 500


@app.get('/api/xero-callback')
def xero_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({ 'message': 'Missing authorization code' }), 400
    try:
        oauth = get_oauth_config()
        headers = {
            'Authorization': build_basic_auth_header(oauth['client_id'], oauth['client_secret']),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': oauth['redirect_uri'],
        }
        resp = requests.post(oauth['token_url'], headers=headers, data=data, timeout=30)
        resp.raise_for_status()
        token_set = resp.json()

        # Fetch connections (tenants)
        access_token = token_set.get('access_token')
        conns_resp = requests.get(oauth['connections_url'], headers=authorized_headers(access_token), timeout=30)
        conns_resp.raise_for_status()
        tenants = conns_resp.json() or []
        first_tenant = tenants[0] if tenants else None

        expires_in = token_set.get('expires_in')
        expires_at = None
        if isinstance(expires_in, (int, float)):
            expires_at = (datetime.now(timezone.utc) + timedelta(seconds=float(expires_in))).timestamp()

        write_saved_tokens({
            'tokenSet': token_set,
            'tenantId': first_tenant.get('tenantId') if first_tenant else None,
            'tenantType': first_tenant.get('tenantType') if first_tenant else None,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'expires_at': expires_at,
        })
        return jsonify({ 'message': 'Xero connected successfully', 'tenantId': (first_tenant or {}).get('tenantId'), 'hint': 'Tokens saved to .data/xero.json.' })
    except Exception as e:
        return jsonify({ 'message': 'Xero OAuth failed', 'error': str(e) }), 500


@app.post('/api/create-xero-invoices')
def create_xero_invoices():
    try:
        oauth = get_oauth_config()
    except Exception as e:
        return jsonify({ 'message': 'Missing Xero client credentials', 'error': str(e) }), 500

    booking = request.get_json(silent=True) or {}
    if 'booking' in booking and isinstance(booking['booking'], dict):
        booking = booking['booking']
    if not booking:
        return jsonify({ 'message': 'Missing booking in request body' }), 400

    def diff_days(start_iso: str, end_iso: str) -> int:
        try:
            start = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_iso.replace('Z', '+00:00'))
        except Exception:
            start = datetime.fromisoformat(start_iso)
            end = datetime.fromisoformat(end_iso)
        ms = (end - start).total_seconds() * 1000
        return max(1, int((ms + 1000 * 60 * 60 * 24 - 1) // (1000 * 60 * 60 * 24)))

    def get_interval_days(freq: str) -> int:
        if freq == '3days':
            return 3
        if freq == '7days':
            return 7
        if freq == '10days':
            return 10
        return 10 ** 9

    total_days = diff_days(booking.get('start_date'), booking.get('end_date'))
    total_amount = float(booking.get('total_cost'))
    frequency = booking.get('payment_frequency', 'once')
    interval_days = get_interval_days(frequency)
    use_single = total_days <= 14 or interval_days >= 10 ** 8

    brand_name = get_env('XERO_BRAND_NAME', 'Aurora Motors')

    invoices = []
    if use_single:
        invoices.append({
            'description': f"{brand_name} Car Rental: {total_days} days",
            'amount': total_amount,
            'dueDate': datetime.fromisoformat(booking.get('start_date').replace('Z', '+00:00')).isoformat(),
        })
    else:
        num_intervals = (total_days + interval_days - 1) // interval_days
        base_amount = total_amount / num_intervals
        start = datetime.fromisoformat(booking.get('start_date').replace('Z', '+00:00'))
        for i in range(num_intervals):
            due = start + timedelta(days=i * interval_days)
            amount = base_amount if i < num_intervals - 1 else round(total_amount - base_amount * (num_intervals - 1), 2)
            invoices.append({
                'description': f"{brand_name} Car Rental: installment {i+1}/{num_intervals}",
                'amount': float(f"{amount:.2f}"),
                'dueDate': due.isoformat(),
            })

    saved = read_saved_tokens() or {}
    token_set = (saved.get('tokenSet') or {})
    access_token = token_set.get('access_token')
    tenant_id = saved.get('tenantId')

    # Support fallback via env if not connected yet
    if not (access_token and tenant_id):
        # Try to use refresh token and/or env provided tenant id
        refresh_token = os.getenv('XERO_REFRESH_TOKEN')
        env_tenant = os.getenv('XERO_TENANT_ID')
        if refresh_token:
            saved = refresh_token_if_needed({'refresh_token': refresh_token, 'tenantId': env_tenant}, oauth)
            token_set = saved.get('tokenSet') or {}
            access_token = token_set.get('access_token')
            tenant_id = saved.get('tenantId') or env_tenant
        else:
            return jsonify({ 'message': 'Xero not connected yet. Visit /api/xero-start to connect.' }), 400

    # Refresh if needed
    saved = refresh_token_if_needed({'tokenSet': token_set, 'tenantId': tenant_id, 'refresh_token': token_set.get('refresh_token')}, oauth)
    token_set = saved.get('tokenSet') or {}
    access_token = token_set.get('access_token')
    tenant_id = saved.get('tenantId') or tenant_id
    if not tenant_id:
        # fetch tenants
        conns_resp = requests.get(oauth['connections_url'], headers=authorized_headers(access_token), timeout=30)
        conns_resp.raise_for_status()
        tenants = conns_resp.json() or []
        tenant_id = (tenants[0] or {}).get('tenantId') if tenants else None
        if tenant_id:
            write_saved_tokens({ **saved, 'tenantId': tenant_id })
    if not tenant_id:
        return jsonify({ 'message': 'No Xero tenant found. Ensure the org is connected.' }), 400

    # Create or ensure contact
    contact_email = booking.get('driver_email')
    contact_name = booking.get('driver_fullname') or contact_email

    contact_create_res = requests.post(
        f"{oauth['api_base']}/Contacts",
        headers=authorized_headers(access_token, tenant_id),
        json={ 'Contacts': [{ 'Name': contact_name, 'EmailAddress': contact_email }] },
        timeout=30,
    )
    if contact_create_res.status_code not in (200, 201):
        return jsonify({ 'message': 'Failed to create contact', 'error': contact_create_res.text }), 500
    contact_body = contact_create_res.json() or {}
    contacts = contact_body.get('Contacts') or []
    contact_id = (contacts[0] or {}).get('ContactID') if contacts else None

    created_count = 0
    for inv in invoices:
        payload = {
            'Invoices': [{
                'Type': 'ACCREC',
                'Contact': { 'ContactID': contact_id } if contact_id else { 'Name': contact_name, 'EmailAddress': contact_email },
                'Date': datetime.now(timezone.utc).date().isoformat(),
                'DueDate': datetime.fromisoformat(inv['dueDate']).date().isoformat(),
                'LineItems': [{
                    'Description': inv['description'],
                    'Quantity': 1,
                    'UnitAmount': float(f"{float(inv['amount']):.2f}"),
                    'AccountCode': '200',
                }],
                'Status': 'AUTHORISED',
            }]
        }
        create_res = requests.post(
            f"{oauth['api_base']}/Invoices",
            headers=authorized_headers(access_token, tenant_id),
            json=payload,
            timeout=30,
        )
        if create_res.status_code not in (200, 201):
            return jsonify({ 'message': 'Failed to create invoice', 'error': create_res.text }), 500
        created = (create_res.json() or {}).get('Invoices') or []
        created_invoice = created[0] if created else None
        if created_invoice and created_invoice.get('InvoiceID'):
            try:
                requests.post(
                    f"{oauth['api_base']}/Invoices/{created_invoice['InvoiceID']}/Email",
                    headers=authorized_headers(access_token, tenant_id),
                    timeout=30,
                )
            except Exception:
                pass
        created_count += 1

    schedule_text = 'single' if use_single else f"every {interval_days} days"
    return jsonify({ 'message': 'Invoices created', 'count': created_count, 'schedule': schedule_text })


# Static assets and SPA fallback
@app.get('/')
def root_index():
    index_path = os.path.join(DIST_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(DIST_DIR, 'index.html')
    return jsonify({ 'message': 'Build not found. Run npm run build.' }), 404


@app.get('/assets/<path:filename>')
def assets(filename: str):
    return send_from_directory(os.path.join(DIST_DIR, 'assets'), filename)


@app.get('/<path:path>')
def spa_fallback(path: str):
    # Serve index.html for SPA routes unless path begins with api/
    if path.startswith('api/'):
        return jsonify({ 'message': 'Not found' }), 404
    index_path = os.path.join(DIST_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(DIST_DIR, 'index.html')
    return jsonify({ 'message': 'Not found' }), 404


if __name__ == '__main__':
    port = int(os.getenv('PORT', '3000'))
    app.run(host='0.0.0.0', port=port)

