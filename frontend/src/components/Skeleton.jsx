import { cn } from '../lib/utils'

export function SkeletonLine({ width = 'w-full', height = 'h-4', className }) {
  return (
    <div
      className={cn(
        'animate-pulse bg-slate-700 rounded',
        width,
        height,
        className
      )}
    />
  )
}

export function SkeletonCard({ className }) {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-800 bg-slate-900 shadow-sm p-6',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="h-8 w-8 rounded-lg animate-pulse bg-slate-700" />
        <SkeletonLine width="w-1/2" height="h-5" />
      </div>
      {/* Lines */}
      <div className="space-y-3">
        <SkeletonLine width="w-full" height="h-4" />
        <SkeletonLine width="w-3/4" height="h-4" />
        <SkeletonLine width="w-1/2" height="h-4" />
      </div>
    </div>
  )
}

export function SkeletonMetricCard({ className }) {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-800 bg-slate-900 shadow-sm p-6',
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        {/* Circle icon placeholder */}
        <div className="h-9 w-9 rounded-lg animate-pulse bg-slate-700" />
        {/* Badge placeholder */}
        <div className="h-5 w-16 rounded-full animate-pulse bg-slate-700" />
      </div>
      {/* Title line */}
      <SkeletonLine width="w-1/2" height="h-4" className="mb-2" />
      {/* Big number placeholder */}
      <div className="h-8 w-24 rounded animate-pulse bg-slate-700 mb-2" />
      {/* Subtitle line */}
      <SkeletonLine width="w-3/4" height="h-3" />
    </div>
  )
}

export function SkeletonTable({ className }) {
  const rows = [0, 1, 2, 3, 4]
  return (
    <div className={cn('rounded-xl border border-slate-800 bg-slate-900 shadow-sm overflow-hidden', className)}>
      {/* Header row */}
      <div className="flex gap-4 p-4 border-b border-slate-800 bg-slate-800">
        <SkeletonLine width="w-1/4" height="h-4" />
        <SkeletonLine width="w-1/4" height="h-4" />
        <SkeletonLine width="w-1/4" height="h-4" />
        <SkeletonLine width="w-1/4" height="h-4" />
      </div>
      {/* Body rows */}
      {rows.map((i) => (
        <div key={i} className="flex gap-4 p-4 border-b border-slate-800 last:border-b-0">
          <SkeletonLine width="w-1/4" height="h-4" />
          <SkeletonLine width="w-1/4" height="h-4" />
          <SkeletonLine width="w-1/4" height="h-4" />
          <SkeletonLine width="w-1/4" height="h-4" />
        </div>
      ))}
    </div>
  )
}
