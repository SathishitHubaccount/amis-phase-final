import { Download } from 'lucide-react'

export default function ExportButton({ endpoint, filename, label = "Export CSV", className = "" }) {
  const handleExport = () => {
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const exportURL = `${baseURL}${endpoint}`

    // Create a temporary link and trigger download
    window.location.href = exportURL
  }

  return (
    <button
      onClick={handleExport}
      className={`px-4 py-2 border border-slate-700 text-slate-300 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2 ${className}`}
    >
      <Download className="h-4 w-4" />
      {label}
    </button>
  )
}
