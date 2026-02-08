/**
 * EmptyState component for consistent empty state displays
 * T070: Reusable component with Sky-Aura Glass aesthetic
 */

import { LucideIcon } from 'lucide-react'
import { Button } from './button'
import { cn } from '@/lib/utils'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4 text-center',
        className
      )}
    >
      <div className="mb-4 rounded-full bg-sky-cyan-500/10 p-4">
        <Icon className="h-8 w-8 text-sky-cyan-400" />
      </div>
      <h3 className="mb-2 text-lg font-medium text-text-primary font-chelsea">
        {title}
      </h3>
      <p className="mb-6 max-w-md text-sm text-text-muted">
        {description}
      </p>
      {action && (
        <Button onClick={action.onClick} className="font-chelsea">
          {action.label}
        </Button>
      )}
    </div>
  )
}
