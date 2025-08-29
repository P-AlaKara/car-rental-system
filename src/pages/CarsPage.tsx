import * as React from 'react'
import Header from '../components/Header'
import Footer from '../components/Footer'
import CarCard from '../components/CarCard'
import { fleetAPI, type CarListResponse } from '../lib/api'

const CARS_PER_PAGE = 12

const Chip = ({ active, children, onClick }: { active: boolean; children: React.ReactNode; onClick: () => void }) => (
  <button
    onClick={onClick}
    className={`px-3 py-1.5 rounded-md text-sm font-medium border transition ${active ? 'bg-sky-600 text-white border-sky-600' : 'bg-white text-slate-700 border-slate-200 hover:border-sky-300'}`}
  >
    {children}
  </button>
)

function CarsPage() {
  const [typeFilter, setTypeFilter] = React.useState<string>('All')
  const [searchQuery, setSearchQuery] = React.useState('')
  const [priceRange, setPriceRange] = React.useState<string>('All')
  const [currentPage, setCurrentPage] = React.useState(1)
  const [cars, setCars] = React.useState<CarListResponse['data']['data']>([])
  const [total, setTotal] = React.useState(0)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const types = ['All', 'Sedan', 'SUV', 'Hatchback', 'Van']
  const priceRanges = ['All', 'Under $50', '$50-$100', 'Over $100']

  // Fetch from frontend cars endpoint; apply only min_price + pagination server-side for now
  const fetchCars = React.useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const minPrice = priceRange === 'Under $50' ? 0 : priceRange === '$50-$100' ? 50 : priceRange === 'Over $100' ? 100 : undefined
      const resp = await fleetAPI.getFrontendCars({ min_price: minPrice, page: currentPage - 1, size: CARS_PER_PAGE })
      setCars(resp.data.data)
      setTotal(resp.data.meta.total)
    } catch (e: any) {
      setError(e?.message || 'Failed to load cars')
    } finally {
      setLoading(false)
    }
  }, [priceRange, currentPage])

  React.useEffect(() => {
    fetchCars()
  }, [fetchCars])

  // Client-side filter for type and search since API doesn't support them yet
  const filteredCars = React.useMemo(() => {
    let filtered = cars
    if (typeFilter !== 'All') filtered = filtered.filter(car => car.category?.name === typeFilter || car.category === typeFilter)
    if (searchQuery) filtered = filtered.filter(car => `${car.make} ${car.model}`.toLowerCase().includes(searchQuery.toLowerCase()))
    return filtered
  }, [cars, typeFilter, searchQuery])

  const totalPages = Math.max(1, Math.ceil((total || filteredCars.length) / CARS_PER_PAGE))
  const paginatedCars = filteredCars

  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Header />
      
      <div className="flex-1">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-semibold text-slate-900 mb-2">Our Fleet</h1>
            <p className="text-slate-600">Choose from our collection of well-maintained vehicles</p>
          </div>

          {/* Filters */}
          <div className="bg-white border rounded-lg p-6 mb-8 space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-900 mb-3">Search</label>
              <input
                type="text"
                placeholder="Search by make or model..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full max-w-md px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-900 mb-3">Vehicle Type</label>
              <div className="flex flex-wrap gap-2">
                {types.map(type => (
                  <Chip key={type} active={typeFilter === type} onClick={() => setTypeFilter(type)}>
                    {type}
                  </Chip>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-900 mb-3">Price Range (per day)</label>
              <div className="flex flex-wrap gap-2">
                {priceRanges.map(range => (
                  <Chip key={range} active={priceRange === range} onClick={() => setPriceRange(range)}>
                    {range}
                  </Chip>
                ))}
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="mb-6">
            {error ? (
              <p className="text-red-600">{error}</p>
            ) : (
              <p className="text-slate-600">
                Showing {paginatedCars.length} of {total || filteredCars.length} vehicles
              </p>
            )}
          </div>

          {/* Cars Grid */}
          {loading ? (
            <div className="text-center py-12 text-slate-600">Loading cars...</div>
          ) : paginatedCars.length > 0 ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
              {paginatedCars.map((car) => (
                <CarCard key={car.id} car={car} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-slate-500 text-lg">No vehicles found matching your criteria.</p>
              <button 
                onClick={() => {
                  setTypeFilter('All')
                  setSearchQuery('')
                  setPriceRange('All')
                }}
                className="mt-4 px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition"
              >
                Clear Filters
              </button>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-2 rounded-md border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-3 py-2 rounded-md border transition ${
                    currentPage === page 
                      ? 'bg-sky-600 text-white border-sky-600' 
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {page}
                </button>
              ))}
              
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-2 rounded-md border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>

      <Footer />
    </main>
  )
}

export default CarsPage
