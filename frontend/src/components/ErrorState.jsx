import { AlertTriangle } from 'lucide-react'

export default function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry,
}) {
  return (
    <div className="flex flex-col items-center justify-center h-96 gap-4 text-center px-4">
      <div className="p-4 bg-red-50 rounded-full">
        <AlertTriangle className="h-12 w-12 text-red-500" />
      </div>
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
        {message && (
          <p className="text-sm text-slate-500 max-w-md">{message}</p>
        )}
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium text-sm"
        >
          Try Again
        </button>
      )}
    </div>
  )
}
