import express from 'express'
import path from 'node:path'
import fs from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { XeroClient } from 'xero-node'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
app.use(express.json())

// Serve static assets from Vite build
const distDir = path.join(__dirname, 'dist')
app.use(express.static(distDir))

// Shared helpers
const DATA_DIR = path.join(process.cwd(), '.data')
const DATA_FILE = path.join(DATA_DIR, 'xero.json')

async function ensureDataDir() {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true })
  } catch {}
}

function createXeroClient() {
  const { XERO_CLIENT_ID, XERO_CLIENT_SECRET, XERO_REDIRECT_URI } = process.env
  if (!XERO_CLIENT_ID || !XERO_CLIENT_SECRET) {
    throw new Error('Missing Xero client credentials')
  }
  const redirectUri = XERO_REDIRECT_URI || 'http://localhost:5173/api/xero-callback'
  return new XeroClient({
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
}

// GET /api/xero-start
app.get('/api/xero-start', async (req, res) => {
  try {
    const xero = createXeroClient()
    await xero.initialize()
    const consentUrl = xero.buildConsentUrl()
    res.redirect(302, consentUrl)
  } catch (err) {
    console.error('xero-start error', err)
    res.status(500).json({ message: 'Failed to start Xero OAuth', error: err?.message || 'Unknown error' })
  }
})

// GET /api/xero-callback
app.get('/api/xero-callback', async (req, res) => {
  const { code } = req.query
  if (!code || typeof code !== 'string') {
    return res.status(400).json({ message: 'Missing authorization code' })
  }
  try {
    const xero = createXeroClient()
    await xero.initialize()
    const redirectUri = (process.env.XERO_REDIRECT_URI || 'http://localhost:5173/api/xero-callback')
    const tokenSet = await xero.apiCallback(`${redirectUri}?code=${encodeURIComponent(code)}`)
    const tenants = await xero.updateTenants()
    const firstTenant = tenants[0]

    await ensureDataDir()
    await fs.writeFile(
      DATA_FILE,
      JSON.stringify({ tokenSet, tenantId: firstTenant?.tenantId, tenantType: firstTenant?.tenantType, createdAt: new Date().toISOString() }, null, 2),
      'utf8'
    )
    res.status(200).json({ message: 'Xero connected successfully', tenantId: firstTenant?.tenantId, hint: 'Tokens saved to .data/xero.json.' })
  } catch (err) {
    console.error('xero-callback error', err)
    res.status(500).json({ message: 'Xero OAuth failed', error: err?.message || 'Unknown error' })
  }
})

// POST /api/create-xero-invoices
app.post('/api/create-xero-invoices', async (req, res) => {
  const {
    XERO_CLIENT_ID,
    XERO_CLIENT_SECRET,
    XERO_REDIRECT_URI,
    XERO_TENANT_ID,
    XERO_REFRESH_TOKEN,
    XERO_BRAND_NAME,
  } = process.env

  if (!XERO_CLIENT_ID || !XERO_CLIENT_SECRET) {
    return res.status(500).json({ message: 'Missing Xero client credentials' })
  }

  const booking = req.body?.booking || req.body
  if (!booking) return res.status(400).json({ message: 'Missing booking in request body' })

  const diffDays = (startISO, endISO) => {
    const start = new Date(startISO)
    const end = new Date(endISO)
    const ms = end.getTime() - start.getTime()
    return Math.max(1, Math.ceil(ms / (1000 * 60 * 60 * 24)))
  }

  const getIntervalDays = (freq) => {
    if (freq === '3days') return 3
    if (freq === '7days') return 7
    if (freq === '10days') return 10
    return Infinity
  }

  const totalDays = diffDays(booking.start_date, booking.end_date)
  const totalAmount = Number(booking.total_cost)
  const frequency = booking.payment_frequency || 'once'
  const intervalDays = getIntervalDays(frequency)
  const useSingle = totalDays <= 14 || intervalDays === Infinity

  const buildLineItem = (description, amount) => ({
    Description: description,
    Quantity: 1,
    UnitAmount: Number(Number(amount).toFixed(2)),
    AccountCode: '200',
  })

  const invoices = []
  if (useSingle) {
    invoices.push({
      description: `${XERO_BRAND_NAME || 'Aurora Motors'} Car Rental: ${totalDays} days`,
      amount: totalAmount,
      dueDate: new Date(booking.start_date).toISOString(),
    })
  } else {
    const numIntervals = Math.ceil(totalDays / intervalDays)
    const baseAmount = totalAmount / numIntervals
    const start = new Date(booking.start_date)
    for (let i = 0; i < numIntervals; i++) {
      const due = new Date(start)
      due.setDate(due.getDate() + i * intervalDays)
      invoices.push({
        description: `${XERO_BRAND_NAME || 'Aurora Motors'} Car Rental: installment ${i + 1}/${numIntervals}`,
        amount: i === numIntervals - 1 ? Number((totalAmount - baseAmount * (numIntervals - 1)).toFixed(2)) : Number(baseAmount.toFixed(2)),
        dueDate: due.toISOString(),
      })
    }
  }

  try {
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

    let tenantId = undefined
    let haveTokens = false
    try {
      const raw = await fs.readFile(DATA_FILE, 'utf8')
      const saved = JSON.parse(raw)
      if (saved?.tokenSet) {
        xero.setTokenSet(saved.tokenSet)
        haveTokens = true
      }
      if (saved?.tenantId) tenantId = saved.tenantId
    } catch {}

    if (!haveTokens && XERO_REFRESH_TOKEN) {
      xero.setTokenSet({
        token_type: 'Bearer',
        scope: 'offline_access accounting.transactions accounting.contacts accounting.settings email',
        access_token: 'dummy',
        refresh_token: XERO_REFRESH_TOKEN,
        expires_at: 0,
        session_state: null,
      })
      haveTokens = true
    }

    if (!haveTokens) {
      return res.status(400).json({ message: 'Xero not connected yet. Visit /api/xero-start to connect.' })
    }

    await xero.refreshToken()

    if (!tenantId) {
      const tenants = await xero.updateTenants()
      tenantId = tenants?.[0]?.tenantId
    }
    if (!tenantId && XERO_TENANT_ID) tenantId = XERO_TENANT_ID
    if (!tenantId) return res.status(400).json({ message: 'No Xero tenant found. Ensure the org is connected.' })

    try {
      await ensureDataDir()
      await fs.writeFile(
        DATA_FILE,
        JSON.stringify({ tokenSet: xero.readTokenSet(), tenantId, updatedAt: new Date().toISOString() }, null, 2),
        'utf8'
      )
    } catch {}

    const contactEmail = booking.driver_email
    const contactName = booking.driver_fullname || booking.driver_email

    const contactCreateRes = await xero.accountingApi.createContacts(tenantId, {
      contacts: [{ name: contactName, emailAddress: contactEmail }],
    })
    const contactId = contactCreateRes.body.contacts?.[0]?.contactID

    const createdInvoices = []
    for (const inv of invoices) {
      const createRes = await xero.accountingApi.createInvoices(tenantId, {
        invoices: [{
          type: 'ACCREC',
          contact: { contactID: contactId },
          date: new Date().toISOString().slice(0, 10),
          dueDate: inv.dueDate.slice(0, 10),
          lineItems: [buildLineItem(inv.description, inv.amount)],
          status: 'AUTHORISED',
        }],
      })
      const created = createRes.body.invoices?.[0]
      createdInvoices.push(created)
      if (created?.invoiceID) {
        try {
          await xero.accountingApi.emailInvoice(tenantId, created.invoiceID)
        } catch (e) {
          console.error('Failed to email invoice', e)
        }
      }
    }

    res.status(200).json({ message: 'Invoices created', count: createdInvoices.length, schedule: useSingle ? 'single' : `every ${intervalDays} days` })
  } catch (err) {
    console.error('create-xero-invoices error', err)
    res.status(500).json({ message: 'Xero integration failed', error: err?.message || 'Unknown error' })
  }
})

// SPA fallback to index.html
app.get('*', async (req, res) => {
  try {
    res.sendFile(path.join(distDir, 'index.html'))
  } catch {
    res.status(404).send('Not found')
  }
})

const port = process.env.PORT || 3000
app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`)
})

