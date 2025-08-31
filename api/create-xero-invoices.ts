import type { VercelRequest, VercelResponse } from '@vercel/node'
import { XeroClient } from 'xero-node'

type PaymentFrequency = 'once' | '3days' | '7days' | '10days'

interface CreateInvoicePayload {
  booking: {
    car_id: number
    start_date: string
    end_date: string
    pickup_location: string
    return_location: string
    driver_email: string
    driver_fullname: string
    license_number: string
    residential_area: string
    special_requests?: string
    total_cost: number
    payment_frequency: PaymentFrequency
  }
  backendBookingResponse?: any
}

function diffDays(startISO: string, endISO: string): number {
  const start = new Date(startISO)
  const end = new Date(endISO)
  const ms = end.getTime() - start.getTime()
  return Math.max(1, Math.ceil(ms / (1000 * 60 * 60 * 24)))
}

function getIntervalDays(freq: PaymentFrequency): number {
  if (freq === '3days') return 3
  if (freq === '7days') return 7
  if (freq === '10days') return 10
  return Infinity
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') return res.status(405).json({ message: 'Method not allowed' })

  const {
    XERO_CLIENT_ID,
    XERO_CLIENT_SECRET,
    XERO_REDIRECT_URI,
    XERO_TENANT_ID,
    XERO_REFRESH_TOKEN,
    XERO_BRAND_NAME
  } = process.env

  if (!XERO_CLIENT_ID || !XERO_CLIENT_SECRET || !XERO_REDIRECT_URI || !XERO_TENANT_ID || !XERO_REFRESH_TOKEN) {
    return res.status(500).json({ message: 'Missing Xero environment configuration' })
  }

  let payload: CreateInvoicePayload
  try {
    payload = req.body as CreateInvoicePayload
  } catch {
    return res.status(400).json({ message: 'Invalid JSON body' })
  }

  const { booking } = payload

  const totalDays = diffDays(booking.start_date, booking.end_date)
  const totalAmount = Number(booking.total_cost)
  const frequency = booking.payment_frequency || 'once'
  const intervalDays = getIntervalDays(frequency)

  // Determine schedule: single invoice if <= 14 days, otherwise by interval
  const useSingle = totalDays <= 14 || intervalDays === Infinity

  // Build line items helper
  const buildLineItem = (description: string, amount: number) => ({
    Description: description,
    Quantity: 1,
    UnitAmount: Number(amount.toFixed(2)),
    AccountCode: '200',
  })

  // Prepare schedule amounts
  let invoices: Array<{ description: string; amount: number; dueDate: string }> = []
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

  // Init Xero client
  const xero = new XeroClient({
    clientId: XERO_CLIENT_ID,
    clientSecret: XERO_CLIENT_SECRET,
    redirectUris: [XERO_REDIRECT_URI],
    scopes: [
      'offline_access',
      'accounting.transactions',
      'accounting.contacts',
      'accounting.settings',
      'email'
    ],
  })

  try {
    // Set the token set with refresh token
    await xero.initialize()
    xero.setTokenSet({
      token_type: 'Bearer',
      scope: 'offline_access accounting.transactions accounting.contacts accounting.settings email',
      access_token: 'dummy',
      refresh_token: XERO_REFRESH_TOKEN,
      expires_at: 0,
      session_state: null as any,
    })
    await xero.refreshToken()

    // Upsert contact by email
    const contactEmail = booking.driver_email
    const contactName = booking.driver_fullname || booking.driver_email

    // Create or find contact
    const contactCreateRes = await xero.accountingApi.createContacts(XERO_TENANT_ID, {
      contacts: [{
        name: contactName,
        emailAddress: contactEmail,
        contacts: undefined,
      } as any],
    })
    const contactId = contactCreateRes.body.contacts?.[0]?.contactID

    // Create invoices and email them
    const createdInvoices: any[] = []
    for (const inv of invoices) {
      const createRes = await xero.accountingApi.createInvoices(XERO_TENANT_ID, {
        invoices: [{
          type: 'ACCREC',
          contact: { contactID: contactId },
          date: new Date().toISOString().slice(0, 10),
          dueDate: inv.dueDate.slice(0, 10),
          lineItems: [buildLineItem(inv.description, inv.amount)],
          status: 'AUTHORISED',
        } as any],
      })
      const created = createRes.body.invoices?.[0]
      createdInvoices.push(created)

      if (created?.invoiceID) {
        // Email invoice via Xero
        try {
          await xero.accountingApi.emailInvoice(XERO_TENANT_ID, created.invoiceID)
        } catch (e) {
          console.error('Failed to email invoice', e)
        }
      }
    }

    return res.status(200).json({
      message: 'Invoices created',
      count: createdInvoices.length,
      schedule: useSingle ? 'single' : `every ${intervalDays} days`,
    })
  } catch (error: any) {
    console.error('Xero error', error?.response?.body || error)
    return res.status(500).json({ message: 'Xero integration failed', error: error?.message || 'Unknown error' })
  }
}

