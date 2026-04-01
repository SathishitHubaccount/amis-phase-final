import { Calendar } from 'lucide-react'

const PRESET_RANGES = [
  { label: 'Last 7 Days', days: 7 },
  { label: 'Last 30 Days', days: 30 },
  { label: 'Last 90 Days', days: 90 },
  { label: 'Last 6 Months', days: 180 },
  { label: 'Last Year', days: 365 },
]

export default function DateRangePicker({ startDate, endDate, onStartChange, onEndChange, className = '' }) {
  const applyPreset = (days) => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - days)

    onStartChange(start.toISOString().split('T')[0])
    onEndChange(end.toISOString().split('T')[0])
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <label className="block text-sm font-medium text-slate-300">
        Date Range
      </label>

      {/* Preset Buttons */}
      <div className="flex flex-wrap gap-2">
        {PRESET_RANGES.map((preset) => (
          <button
            key={preset.label}
            onClick={() => applyPreset(preset.days)}
            className="px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 rounded-md hover:bg-slate-700 transition-colors"
          >
            {preset.label}
          </button>
        ))}
      </div>

      {/* Custom Date Inputs */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-slate-400 mb-1">From</label>
          <div className="relative">
            <input
              type="date"
              value={startDate}
              onChange={(e) => onStartChange(e.target.value)}
              className="w-full pl-9 pr-3 py-2 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <Calendar className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none" />
          </div>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">To</label>
          <div className="relative">
            <input
              type="date"
              value={endDate}
              onChange={(e) => onEndChange(e.target.value)}
              className="w-full pl-9 pr-3 py-2 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <Calendar className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none" />
          </div>
        </div>
      </div>
    </div>
  )
}
