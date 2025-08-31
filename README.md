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

## Environment (for Xero invoices)

Deploy with these environment variables configured (e.g., in Vercel project settings):

- `XERO_CLIENT_ID`
- `XERO_CLIENT_SECRET`
- `XERO_REDIRECT_URI` (can be any valid URL for server-to-server refresh, e.g., `https://example.com/callback`)
- `XERO_TENANT_ID`
- `XERO_REFRESH_TOKEN` (must be kept fresh with your app’s OAuth flow)
- `XERO_BRAND_NAME` (optional branding in invoice descriptions)

Serverless function: `api/create-xero-invoices.ts` creates invoices and emails them via Xero after a booking is created. Logic:

- If booking length ≤ 14 days, a single invoice is created and emailed.
- If > 14 days, invoices are split by the selected schedule (every 3/7/10 days).

## Development

The project uses a modular structure with:
- `src/components/` - Reusable UI components
- `src/lib/` - Utilities and data management
- `src/App.tsx` - Main application with routing

## Demo Data

The application uses mock data for demonstration purposes. In a production environment, this would be replaced with a real API backend.
