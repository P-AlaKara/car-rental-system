import type { VercelRequest, VercelResponse } from '@vercel/node'
import { XeroClient } from 'xero-node'
import fs from 'node:fs/promises'
import path from 'node:path'

const DATA_DIR = path.join(process.cwd(), '.data')
const DATA_FILE = path.join(DATA_DIR, 'xero.json')

async function ensureDataDir(): Promise<void> {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true })
  } catch {}
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { XERO_CLIENT_ID, XERO_CLIENT_SECRET, XERO_REDIRECT_URI } = process.env
  if (!XERO_CLIENT_ID || !XERO_CLIENT_SECRET) {
    return res.status(500).json({ message: 'Missing Xero client credentials' })
  }

  const redirectUri = XERO_REDIRECT_URI || 'http://localhost:5173/api/xero-callback'

  const { code } = req.query as { code?: string }
  if (!code) {
    return res.status(400).json({ message: 'Missing authorization code' })
  }

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

  try {
    await xero.initialize()
    const tokenSet = await xero.apiCallback(`${redirectUri}?code=${encodeURIComponent(code)}`)

    // Fetch connections to get tenantId
    const conns = await xero.updateTenants()
    const firstTenant = conns[0]

    await ensureDataDir()
    const persist = {
      tokenSet,
      tenantId: firstTenant?.tenantId,
      tenantType: firstTenant?.tenantType,
      createdAt: new Date().toISOString(),
    }
    await fs.writeFile(DATA_FILE, JSON.stringify(persist, null, 2), 'utf8')

    return res.status(200).json({
      message: 'Xero connected successfully',
      tenantId: firstTenant?.tenantId,
      hint: 'Tokens saved to .data/xero.json. You can now create invoices.',
    })
  } catch (err: any) {
    console.error('Xero OAuth callback error', err?.response?.body || err)
    return res.status(500).json({ message: 'Xero OAuth failed', error: err?.message || 'Unknown error' })
  }
}

