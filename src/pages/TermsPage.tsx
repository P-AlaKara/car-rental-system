import Header from '../components/Header'
import Footer from '../components/Footer'

function TermsPage() {
  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Header />
      
      <div className="flex-1">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold text-slate-900 mb-8">Terms and Conditions</h1>
            
            <div className="prose prose-lg max-w-none">
              <p className="text-slate-600 mb-8">
                Last updated: {new Date().toLocaleDateString()}
              </p>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">1. Agreement Overview</h2>
                <p className="text-slate-700 mb-4">
                  These Terms and Conditions ("Terms") govern your use of Smart Car Rentals services. 
                  By booking a vehicle with us, you agree to be bound by these Terms.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">2. Rental Requirements</h2>
                <ul className="list-disc list-inside text-slate-700 space-y-2">
                  <li>Valid driver's license held for at least 1 year</li>
                  <li>Minimum age of 21 years (additional fees may apply for drivers under 25)</li>
                  <li>Valid credit card for security deposit</li>
                  <li>Proof of identity (passport or driver's license)</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">3. Vehicle Use</h2>
                <p className="text-slate-700 mb-4">
                  The rental vehicle must be used in accordance with the following conditions:
                </p>
                <ul className="list-disc list-inside text-slate-700 space-y-2">
                  <li>Only authorized drivers may operate the vehicle</li>
                  <li>Vehicle must not be used for commercial purposes unless specifically agreed</li>
                  <li>No smoking, pets, or illegal activities in the vehicle</li>
                  <li>Vehicle must not be taken outside of agreed geographical boundaries</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">4. Payment and Fees</h2>
                <ul className="list-disc list-inside text-slate-700 space-y-2">
                  <li>Rental fees are due at the time of booking or pickup</li>
                  <li>Security deposit will be held on your credit card</li>
                  <li>Additional charges may apply for late returns, cleaning, or damage</li>
                  <li>Fuel must be returned at the same level as pickup</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">5. Insurance and Liability</h2>
                <p className="text-slate-700 mb-4">
                  Basic insurance is included with all rentals. Additional coverage options are available. 
                  The renter is responsible for:
                </p>
                <ul className="list-disc list-inside text-slate-700 space-y-2">
                  <li>Any damage not covered by insurance</li>
                  <li>Traffic fines and parking tickets</li>
                  <li>Loss or theft of vehicle keys</li>
                  <li>Towing and impound fees</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">6. Cancellation Policy</h2>
                <ul className="list-disc list-inside text-slate-700 space-y-2">
                  <li>Free cancellation up to 24 hours before pickup</li>
                  <li>Cancellations within 24 hours may incur charges</li>
                  <li>No-shows will be charged the full rental amount</li>
                  <li>Refunds processed within 5-7 business days</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">7. Vehicle Return</h2>
                <p className="text-slate-700 mb-4">
                  Vehicles must be returned:
                </p>
                <ul className="list-disc list-inside text-slate-700 space-y-2">
                  <li>At the agreed date, time, and location</li>
                  <li>In the same condition as received</li>
                  <li>With the same fuel level</li>
                  <li>With all accessories and documents</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">8. Prohibited Uses</h2>
                <p className="text-slate-700 mb-4">
                  The following are strictly prohibited:
                </p>
                <ul className="list-disc list-inside text-slate-700 space-y-2">
                  <li>Racing, rallying, or competitive driving</li>
                  <li>Towing or pushing other vehicles</li>
                  <li>Transporting hazardous materials</li>
                  <li>Using vehicle under the influence of alcohol or drugs</li>
                  <li>Subletting or transferring the rental to third parties</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">9. Privacy Policy</h2>
                <p className="text-slate-700 mb-4">
                  We collect and use personal information in accordance with our Privacy Policy. 
                  We may share information with third parties as required by law or for business purposes.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">10. Limitation of Liability</h2>
                <p className="text-slate-700 mb-4">
                  Smart Car Rentals' liability is limited to the maximum extent permitted by law. 
                  We are not liable for indirect, consequential, or punitive damages.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">11. Changes to Terms</h2>
                <p className="text-slate-700 mb-4">
                  We reserve the right to modify these Terms at any time. Changes will be effective 
                  immediately upon posting on our website.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-900 mb-4">12. Contact Information</h2>
                <p className="text-slate-700 mb-4">
                  For questions about these Terms, please contact us:
                </p>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <p className="text-slate-700">
                    <strong>Smart Car Rentals</strong><br />
                    123 Collins Street<br />
                    Melbourne VIC 3000<br />
                    Email: legal@smartcarrentals.com.au<br />
                    Phone: 0420 759 910
                  </p>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}

export default TermsPage
