import * as React from 'react'
import Header from '../components/Header'
import Footer from '../components/Footer'
import CarCard from '../components/CarCard'
import { fleetAPI, type CarListResponse } from '../lib/api'

const Badge = ({ children }: { children: React.ReactNode }) => (
  <span className="inline-flex items-center rounded-full bg-white/60 backdrop-blur px-3 py-1 text-xs font-medium text-sky-700 ring-1 ring-sky-100">{children}</span>
)

const SectionContainer = ({ children, className = '', ...props }: React.ComponentProps<'section'>) => (
  <section {...props} className={"container mx-auto px-4 " + className}>{children}</section>
)

const HeroBackground = () => (
  <div className="absolute inset-0">
    {/* Background image layer from clone */}
    <div className="absolute inset-0 bg-[url('/images/hero-light-blue-2.png')] bg-cover bg-center" />
    {/* Soft gradient overlay */}
    <div className="absolute inset-0 bg-gradient-to-br from-sky-200/40 via-sky-100/30 to-white/80" />
    <svg
      className="absolute inset-x-0 top-[22%] w-full h-[55%]"
      viewBox="0 0 1440 320"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="waveA" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#93c5fd" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#60a5fa" stopOpacity="0.35" />
        </linearGradient>
        <linearGradient id="waveB" x1="1" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.28" />
          <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.18" />
        </linearGradient>
      </defs>
      <path fill="url(#waveA)" d="M0,160L48,149.3C96,139,192,117,288,128C384,139,480,181,576,197.3C672,213,768,203,864,176C960,149,1056,107,1152,101.3C1248,96,1344,128,1392,144L1440,160L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z" />
      <path fill="url(#waveB)" d="M0,224L48,208C96,192,192,160,288,149.3C384,139,480,149,576,165.3C672,181,768,203,864,197.3C960,192,1056,160,1152,149.3C1248,139,1344,149,1392,154.7L1440,160L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z" />
    </svg>
    <div className="absolute inset-x-0 bottom-0 h-1/2 bg-[radial-gradient(80%_60%_at_60%_80%,rgba(56,189,248,0.25),transparent_60%)]" />
    </div>
  )

function HomePage() {
  const [featuredCars, setFeaturedCars] = React.useState<CarListResponse['data']['data']>([])
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const fetchFeaturedCars = async () => {
      try {
        setLoading(true)
        setError(null)
        const resp = await fleetAPI.getFrontendCars({ page: 0, size: 4 })
        setFeaturedCars(resp.data.data)
      } catch (e: any) {
        setError(e?.message || 'Failed to load featured cars')
        console.error('Error fetching featured cars:', e)
      } finally {
        setLoading(false)
      }
    }

    fetchFeaturedCars()
  }, [])

  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Header />

      {/* Hero */}
      <section className="relative">
        <HeroBackground />
        <SectionContainer className="relative py-24 md:py-32">
          <div className="max-w-2xl space-y-6">
            <Badge>Melbourne • Rideshare • Long-term • Private</Badge>
            <h1 className="text-4xl md:text-6xl font-semibold leading-tight text-slate-900">
              Drive Smart, <span className="text-sky-700">Rent Smart.</span>
            </h1>
            <p className="text-slate-700">Affordable, reliable, and flexible rentals for rideshare, private use, and long-term customers.</p>
            <div className="flex gap-3">
              <a href="#cars" className="h-10 px-5 inline-flex items-center justify-center rounded-md bg-sky-600 hover:bg-sky-700 text-white shadow-md text-sm">Browse Cars</a>
              <a href="#about" className="h-10 px-5 inline-flex items-center justify-center rounded-md border hover:border-sky-300 bg-transparent text-sm">Learn More</a>
            </div>
          </div>
          <div className="mt-10 -mx-4 px-4 md:hidden">
            <div className="flex gap-2 overflow-x-auto">
              {['SUV', 'Sedan', 'Hatchback', 'Van'].map((c) => (
                <a key={c} href="#cars" className="shrink-0 rounded-md border bg-white/80 px-3 py-2 text-sm font-medium text-slate-800 hover:shadow-sm">
                  {c}
                </a>
              ))}
            </div>
          </div>

          <div className="mt-10 hidden md:grid grid-cols-2 gap-2 max-w-xl">
            {['SUV', 'Sedan', 'Hatchback', 'Van'].map((c) => (
              <a key={c} href="#cars" className="group">
                <div className="rounded-lg border bg-white/70 backdrop-blur transition hover:shadow-md">
                  <div className="p-3 flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-800">{c}</span>
                    <span className="text-xs text-sky-700 group-hover:underline">Explore →</span>
                  </div>
                </div>
              </a>
            ))}
          </div>
        </SectionContainer>
      </section>

      {/* Featured vehicles */}
      <SectionContainer className="py-12 md:py-16" id="cars">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h2 className="text-2xl md:text-3xl font-semibold text-slate-900">Featured vehicles</h2>
            <p className="text-slate-600">Popular choices for our customers</p>
          </div>
          <a href="/cars" className="w-fit h-10 px-5 inline-flex items-center justify-center rounded-md border hover:border-sky-300 bg-white text-sm font-medium">
            View all cars →
          </a>
        </div>

        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-slate-100 rounded-lg p-4 animate-pulse">
                <div className="w-full h-32 bg-slate-200 rounded mb-3"></div>
                <div className="h-4 bg-slate-200 rounded mb-2"></div>
                <div className="h-3 bg-slate-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">Failed to load featured cars: {error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition"
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && featuredCars.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredCars.map((car) => (
              <CarCard key={car.id} car={car} />
            ))}
          </div>
        )}

        {!loading && !error && featuredCars.length === 0 && (
          <div className="text-center py-8">
            <p className="text-slate-600">No featured cars available at the moment.</p>
          </div>
        )}
      </SectionContainer>

      {/* About Section */}
      <SectionContainer className="py-12 md:py-16 bg-sky-50/40" id="about">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-semibold text-slate-900 mb-4">About Smart Car Rentals</h2>
          <p className="text-lg md:text-xl text-slate-600 max-w-3xl mx-auto">
            Your trusted partner for reliable and affordable car rentals in Melbourne. 
            We specialize in rideshare, private use, and long-term rental solutions.
          </p>
        </div>

        {/* Our Story */}
        <div className="mb-16">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-2xl md:text-3xl font-semibold text-slate-900 mb-6 text-center">Our Story</h3>
            <div className="prose prose-lg max-w-none text-slate-700 space-y-6">
              <p>
                Founded in Melbourne, Smart Car Rentals was born from the simple idea that car rental 
                should be accessible, affordable, and hassle-free. We recognized the growing need for 
                flexible transportation solutions in the rideshare economy and set out to create a 
                service that meets the diverse needs of modern drivers.
              </p>
              <p>
                Our journey began with a small fleet of well-maintained vehicles and a commitment to 
                exceptional customer service. Today, we've grown to become one of Melbourne's most 
                trusted car rental services, serving thousands of satisfied customers across the city.
              </p>
              <p>
                Whether you're a rideshare driver looking for a reliable vehicle, a family needing 
                a car for the weekend, or a business requiring long-term rental solutions, we're here 
                to help you get where you need to go.
              </p>
            </div>
          </div>
        </div>

        {/* Our Mission */}
        <div className="bg-white rounded-lg p-8 mb-16 shadow-sm">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-2xl md:text-3xl font-semibold text-slate-900 mb-6">Our Mission</h3>
            <p className="text-lg text-slate-700 mb-8">
              To provide reliable, affordable, and convenient car rental services that empower 
              our customers to achieve their personal and professional goals while maintaining 
              the highest standards of safety and customer satisfaction.
            </p>
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <div className="w-16 h-16 bg-sky-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 className="text-xl font-semibold text-slate-900 mb-2">Reliability</h4>
                <p className="text-slate-600">Dependable vehicles and service you can count on</p>
              </div>
              <div>
                <div className="w-16 h-16 bg-sky-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
                <h4 className="text-xl font-semibold text-slate-900 mb-2">Affordability</h4>
                <p className="text-slate-600">Competitive pricing without compromising quality</p>
              </div>
              <div>
                <div className="w-16 h-16 bg-sky-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <h4 className="text-xl font-semibold text-slate-900 mb-2">Customer Care</h4>
                <p className="text-slate-600">Exceptional service and support every step of the way</p>
              </div>
            </div>
          </div>
        </div>

        {/* Why Choose Us */}
        <div className="mb-16">
          <h3 className="text-2xl md:text-3xl font-semibold text-slate-900 mb-8 text-center">Why Choose Us?</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-slate-900 mb-2">Quality Fleet</h4>
              <p className="text-sm text-slate-600">Well-maintained vehicles with regular servicing</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-slate-900 mb-2">24/7 Support</h4>
              <p className="text-sm text-slate-600">Round-the-clock assistance when you need it</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-slate-900 mb-2">Quick Booking</h4>
              <p className="text-sm text-slate-600">Simple online booking with instant confirmation</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-slate-900 mb-2">Flexible Options</h4>
              <p className="text-sm text-slate-600">Daily, weekly, and monthly rental options</p>
            </div>
          </div>
        </div>


      </SectionContainer>

      {/* Contact Section */}
      <SectionContainer className="py-12 md:py-16" id="contact">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl md:text-3xl font-semibold text-slate-900 mb-4">Contact Us</h2>
            <p className="text-slate-600">Get in touch with our team. We're here to help with all your car rental needs.</p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            {/* Contact Form */}
            <div>
              <h3 className="text-xl font-semibold text-slate-900 mb-6">Send us a message</h3>
              <form className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Full Name *</label>
                    <input
                      type="text"
                      required
                      className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Email Address *</label>
                    <input
                      type="email"
                      required
                      className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Phone Number</label>
                  <input
                    type="tel"
                    className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Subject *</label>
                  <select
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                  >
                    <option value="">Select a subject</option>
                    <option value="booking">Booking Inquiry</option>
                    <option value="support">Customer Support</option>
                    <option value="fleet">Fleet Information</option>
                    <option value="pricing">Pricing Questions</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Message *</label>
                  <textarea
                    rows={6}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                    placeholder="Please provide details about your inquiry..."
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition font-medium"
                >
                  Send Message
                </button>
              </form>
            </div>

            {/* Contact Information */}
            <div>
              <h3 className="text-xl font-semibold text-slate-900 mb-6">Get in touch</h3>
              
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-sky-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-1">Our Location</h4>
                    <p className="text-slate-600">
                      123 Collins Street<br />
                      Melbourne VIC 3000<br />
                      Australia
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-sky-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-1">Phone</h4>
                    <p className="text-slate-600">
                      <a href="tel:+61420759910" className="hover:text-sky-600 transition">
                        0420 759 910
                      </a>
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-sky-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-1">Email</h4>
                    <p className="text-slate-600">
                      <a href="mailto:info@smartcarrentals.com.au" className="hover:text-sky-600 transition">
                        info@smartcarrentals.com.au
                      </a>
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-sky-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-1">Business Hours</h4>
                    <p className="text-slate-600">
                      Monday - Friday: 8:00 AM - 6:00 PM<br />
                      Saturday: 9:00 AM - 4:00 PM<br />
                      Sunday: 10:00 AM - 2:00 PM
                    </p>
                  </div>
                </div>
              </div>

              {/* Emergency Contact */}
              <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.732 0L3.5 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <h4 className="font-semibold text-red-900">24/7 Emergency Support</h4>
                </div>
                <p className="text-red-700 text-sm">
                  For urgent issues during your rental, call our emergency line:
                </p>
                <p className="text-red-900 font-semibold">
                  <a href="tel:+61420759910" className="hover:underline">0420 759 910</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </SectionContainer>

      <Footer />
    </main>
  )
}

export default HomePage
