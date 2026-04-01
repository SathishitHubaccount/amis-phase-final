import { Truck, TrendingUp, AlertTriangle, DollarSign, Award, FileText, MapPin } from 'lucide-react'
import Modal from './Modal'
import Badge from './Badge'

export default function SupplierDetailModal({ isOpen, onClose, supplier }) {
  if (!supplier) return null

  const getRatingColor = (rating) => {
    if (rating === 'A') return 'success'
    if (rating.startsWith('B')) return 'warning'
    return 'error'
  }

  const getRiskColor = (risk) => {
    if (risk === 'Low') return 'text-green-600 bg-green-50'
    if (risk === 'Medium') return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Supplier Details: ${supplier.id}`} size="lg">
      <div className="space-y-6">
        {/* Header Info */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-2xl font-bold text-white">{supplier.name}</h3>
            <div className="flex items-center gap-2 mt-1">
              <MapPin className="h-4 w-4 text-slate-500" />
              <p className="text-sm text-slate-400">{supplier.location}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`px-4 py-2 rounded-lg font-semibold ${getRiskColor(supplier.risk)}`}>
              {supplier.risk} Risk
            </div>
            <div className="text-center">
              <Badge variant={getRatingColor(supplier.rating)} className="text-lg px-4 py-2">
                {supplier.rating}
              </Badge>
            </div>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-600 font-medium">Overall Score</p>
            <p className="text-3xl font-bold text-blue-900 mt-1">{supplier.score}</p>
            <p className="text-xs text-blue-600 mt-1">out of 100</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-green-600 font-medium">On-Time</p>
            <p className="text-3xl font-bold text-green-900 mt-1">{supplier.onTimeDelivery}%</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-sm text-purple-600 font-medium">Quality</p>
            <p className="text-3xl font-bold text-purple-900 mt-1">{supplier.quality}%</p>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <p className="text-sm text-orange-600 font-medium">Cost Index</p>
            <p className="text-3xl font-bold text-orange-900 mt-1">{supplier.costIndex}</p>
          </div>
        </div>

        {/* Commercial Terms */}
        <div>
          <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-green-600" />
            Commercial Terms
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Base Cost</p>
              <p className="text-lg font-bold text-white">${supplier.baseCost}/unit</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">MOQ</p>
              <p className="text-lg font-bold text-white">{supplier.moq.toLocaleString()} units</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Lead Time</p>
              <p className="text-lg font-bold text-white">{supplier.leadTime} ± {supplier.leadTimeVariability} days</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Payment Terms</p>
              <p className="text-lg font-bold text-white">{supplier.paymentTerms}</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Currency</p>
              <p className="text-lg font-bold text-white">{supplier.currency}</p>
            </div>
          </div>
        </div>

        {/* Certifications */}
        <div>
          <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
            <Award className="h-5 w-5 text-blue-600" />
            Certifications
          </h4>
          <div className="flex flex-wrap gap-2">
            {supplier.certifications.map((cert, idx) => (
              <Badge key={idx} variant="info" className="px-3 py-1">
                {cert}
              </Badge>
            ))}
          </div>
        </div>

        {/* Active Contracts */}
        {supplier.contracts && supplier.contracts.length > 0 && (
          <div>
            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <FileText className="h-5 w-5 text-purple-600" />
              Active Contracts
            </h4>
            <div className="space-y-2">
              {supplier.contracts.map((contract) => (
                <div key={contract.id} className="p-3 bg-slate-800 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{contract.id}</span>
                        <Badge variant={contract.status === 'active' ? 'success' : 'warning'}>
                          {contract.status.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 mt-2 text-sm text-slate-400">
                        <div>
                          <span className="text-xs text-slate-500">Period:</span>
                          <p className="font-medium text-white">{contract.startDate} to {contract.endDate}</p>
                        </div>
                        <div>
                          <span className="text-xs text-slate-500">Volume:</span>
                          <p className="font-medium text-white">{contract.volume.toLocaleString()} units</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Incident History */}
        {supplier.incidents && supplier.incidents.length > 0 && (
          <div>
            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Incident History ({supplier.incidents.length})
            </h4>
            <div className="space-y-2">
              {supplier.incidents.map((incident, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border-l-4 ${
                    incident.severity === 'high' ? 'bg-red-50 border-red-500' :
                    incident.severity === 'medium' ? 'bg-yellow-50 border-yellow-500' :
                    'bg-blue-50 border-blue-500'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant={
                          incident.severity === 'high' ? 'error' :
                          incident.severity === 'medium' ? 'warning' :
                          'info'
                        }>
                          {incident.type.toUpperCase()}
                        </Badge>
                        <span className="text-sm font-medium text-white">{incident.date}</span>
                      </div>
                      <p className="text-sm text-slate-300 mt-1">{incident.resolution}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Trend (Mock) */}
        <div>
          <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            Performance Trend
          </h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Last 30 Days</p>
              <p className="text-lg font-bold text-green-600">{supplier.onTimeDelivery}%</p>
              <p className="text-xs text-green-600 mt-1">↑ 2%</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Last 90 Days</p>
              <p className="text-lg font-bold text-green-600">{Math.max(supplier.onTimeDelivery - 3, 70)}%</p>
              <p className="text-xs text-red-600 mt-1">↓ 1%</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Last Year</p>
              <p className="text-lg font-bold text-white">{Math.max(supplier.onTimeDelivery - 5, 65)}%</p>
              <p className="text-xs text-slate-400 mt-1">→ 0%</p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-slate-800">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 border border-slate-700 text-slate-300 rounded-lg font-medium hover:bg-slate-800 transition-colors"
          >
            Close
          </button>
          <button
            onClick={() => {
              alert('Purchase Order creation would be implemented here with ERP integration')
            }}
            className="flex-1 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 transition-all shadow-lg shadow-primary-500/30 flex items-center justify-center gap-2"
          >
            <FileText className="h-5 w-5" />
              Create Purchase Order
            </button>
          </div>
        </div>
      </Modal>
    )
  }
