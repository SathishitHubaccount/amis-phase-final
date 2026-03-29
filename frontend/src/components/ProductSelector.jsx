import { ChevronDown, Package } from 'lucide-react'

const PRODUCTS = [
  { id: 'PROD-A', name: 'Automotive Sensor Unit', category: 'Electronics', status: 'active' },
  { id: 'PROD-B', name: 'Industrial Motor Assembly', category: 'Mechanical', status: 'active' },
  { id: 'PROD-C', name: 'Smart Thermostat', category: 'Electronics', status: 'active' },
  { id: 'PROD-D', name: 'Hydraulic Pump', category: 'Mechanical', status: 'active' },
  { id: 'PROD-E', name: 'LED Display Panel', category: 'Electronics', status: 'limited' },
]

export default function ProductSelector({ value, onChange, className = '' }) {
  const selectedProduct = PRODUCTS.find(p => p.id === value) || PRODUCTS[0]

  return (
    <div className={`relative ${className}`}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Select Product
      </label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full pl-10 pr-10 py-2.5 bg-white border border-gray-300 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 cursor-pointer hover:border-gray-400 transition-colors"
        >
          {PRODUCTS.map((product) => (
            <option key={product.id} value={product.id}>
              {product.id} - {product.name}
            </option>
          ))}
        </select>
        <Package className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
      </div>
      <p className="mt-1 text-xs text-gray-500">
        Category: {selectedProduct.category} • Status: <span className={selectedProduct.status === 'active' ? 'text-green-600' : 'text-orange-600'}>{selectedProduct.status}</span>
      </p>
    </div>
  )
}

export { PRODUCTS }
