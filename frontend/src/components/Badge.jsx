import { cn } from '../lib/utils'

export default function Badge({ children, variant = 'default', className, ...props }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        {
          'bg-slate-800 text-slate-300': variant === 'default',
          'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25': variant === 'success',
          'bg-amber-500/15 text-amber-400 border border-amber-500/25': variant === 'warning',
          'bg-red-500/15 text-red-400 border border-red-500/25': variant === 'error',
          'bg-blue-500/15 text-blue-400 border border-blue-500/25': variant === 'info',
        },
        className
      )}
      {...props}
    >
      {children}
    </span>
  )
}
