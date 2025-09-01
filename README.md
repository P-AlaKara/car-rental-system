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
- Local storage for demo data persistence

## Xero setup (OAuth + tokens)

Environment variables (set in Vercel Project Settings):

- `XERO_CLIENT_ID`
- `XERO_CLIENT_SECRET`
- `XERO_REDIRECT_URI` (recommended: your deployed callback URL)
- `XERO_BRAND_NAME` (optional branding in invoice descriptions)

Recommended redirect URIs to register in your Xero app:

- Production: `https://YOUR-VERCEL-DOMAIN/api/xero-callback`
- Local dev (optional): `http://localhost:5173/api/xero-callback`

First-time connect flow:

1. Ensure `XERO_CLIENT_ID` and `XERO_CLIENT_SECRET` are set.
2. Optionally set `XERO_REDIRECT_URI` to the same value you registered (e.g., `https://YOUR-VERCEL-DOMAIN/api/xero-callback`). If not set, local default `http://localhost:5173/api/xero-callback` is used.
3. Visit `/api/xero-start` to open the Xero consent screen.
4. Approve the app; you will be redirected to `/api/xero-callback` which exchanges the code, fetches your tenant, and stores tokens at `.data/xero.json` (ignored by git).
5. Subsequent API calls will refresh and persist tokens automatically; no need to re-authorize.

Notes:

- If running locally without Vercel CLI, the `/api/*` serverless routes are only available after deploy. Prefer testing the connect flow on your deployed URL.
- If you already have a refresh token and tenant ID from elsewhere, you can still set `XERO_REFRESH_TOKEN` and `XERO_TENANT_ID` temporarily; the app will use them as a fallback and persist refreshed tokens to `.data/xero.json`.

Serverless function `api/create-xero-invoices.ts` creates and emails invoices via Xero. Logic:

- If booking length ≤ 14 days, a single invoice is created and emailed.
- If > 14 days, invoices are split by the selected schedule (every 3/7/10 days).

## Development

The project uses a modular structure with:
- `src/components/` - Reusable UI components
- `src/lib/` - Utilities and data management
- `src/App.tsx` - Main application with routing

## Demo Data

The application uses mock data for demonstration purposes. In a production environment, this would be replaced with a real API backend.
