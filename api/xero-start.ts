import type { VercelRequest, VercelResponse } from '@vercel/node'
import { XeroClient } from 'xero-node'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { XERO_CLIENT_ID, XERO_CLIENT_SECRET, XERO_REDIRECT_URI } = process.env

  if (!XERO_CLIENT_ID || !XERO_CLIENT_SECRET) {
    return res.status(500).json({ message: 'Missing Xero client credentials' })
  }

  // Provide a sensible default redirect for local if not set
  const redirectUri = XERO_REDIRECT_URI || 'http://localhost:5173/api/xero-callback'

  const xero = new XeroClient({
    clientId: XERO_CLIENT_ID,
    clientSecret: XERO_CLIENT_SECRET,
    redirectUris: [redirectUri],
    scopes: [
      'offline_access',
      'accounting.transactions',
      'accounting.contacts',
      'accounting.settings',
      'email',
    ],
  })

  await xero.initialize()
  const consentUrl = xero.buildConsentUrl()

  // Redirect user to Xero consent
  res.status(302).setHeader('Location', consentUrl).end()
}

