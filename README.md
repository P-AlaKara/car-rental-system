# Aurora Motors - Car Rental Platform

A modern car rental platform built with React, TypeScript, and Vite. Features include:

- Browse and filter available vehicles
- Book cars with flexible date selection
- User authentication and profile management
- Responsive design with Tailwind CSS

## Getting Started

```bash
npm install
npm run dev
```

## Backend (Flask)

This project now serves the frontend build and API via a Python Flask server (`app.py`).

- Build frontend assets:
```bash
npm run build
```
- Run Flask locally:
```bash
python3 app.py
```
- Environment variables required for Xero:
  - `XERO_CLIENT_ID`
  - `XERO_CLIENT_SECRET`
  - `XERO_REDIRECT_URI` (recommended: your deployed callback URL)
  - Optional: `XERO_BRAND_NAME`, `XERO_TENANT_ID`, `XERO_REFRESH_TOKEN`

The Flask server exposes:
- `GET /api/xero-start`
- `GET /api/xero-callback`
- `POST /api/create-xero-invoices`

## Features

- **Vehicle Catalog**: Browse cars by category, make, transmission, fuel type, and price
- **Booking System**: Reserve vehicles with date/time selection and extras
- **User Management**: Register, login, and view booking history
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- React 19 with TypeScript
- Vite for fast development and building
- Tailwind CSS v4 for styling
- React Router for navigation
- Flask for API and static serving

## Xero setup (OAuth + tokens)

Environment variables (set in your deployment):

- `XERO_CLIENT_ID`
- `XERO_CLIENT_SECRET`
- `XERO_REDIRECT_URI` (recommended: your deployed callback URL)
- `XERO_BRAND_NAME` (optional branding in invoice descriptions)

Recommended redirect URIs to register in your Xero app:

- Production: `https://YOUR-DEPLOYMENT-DOMAIN/api/xero-callback`
- Local dev (optional): `http://localhost:3000/api/xero-callback`

First-time connect flow:

1. Ensure `XERO_CLIENT_ID` and `XERO_CLIENT_SECRET` are set.
2. Visit `/api/xero-start` to open the Xero consent screen.
3. Approve; you will be redirected to `/api/xero-callback` which exchanges the code, fetches your tenant, and stores tokens at `.data/xero.json`.
4. Subsequent API calls will refresh and persist tokens automatically.

Notes:

- If you already have a refresh token and tenant ID from elsewhere, you can still set `XERO_REFRESH_TOKEN` and `XERO_TENANT_ID` temporarily; the app will use them as a fallback and persist refreshed tokens to `.data/xero.json`.

Server function `POST /api/create-xero-invoices` creates and emails invoices via Xero. Logic:

- If booking length ≤ 14 days, a single invoice is created and emailed.
- If > 14 days, invoices are split by the selected schedule (every 3/7/10 days).

## Development

The project uses a modular structure with:
- `src/components/` - Reusable UI components
- `src/lib/` - Utilities and data management
- `src/App.tsx` - Main application with routing

## Demo Data

The application uses mock data for demonstration purposes. In a production environment, this would be replaced with a real API backend.
