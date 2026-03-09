'use client'

import { Loader2, CheckCircle2, XCircle, Radio } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { ConnectionState } from '@/lib/api/contracts/agent'

interface StatusIndicatorProps {
  state: ConnectionState
  className?: string
}

/**
 * State configuration for the StatusIndicator component
 * Maps each connection state to its icon, label, and styling
 */
const stateConfig: Record<
  ConnectionState,
  {
    icon: typeof Radio
    label: string
    containerClass: string
    iconClass: string
    animate: boolean
  }
> = {
  disconnected: {
    icon: Radio,
    label: 'Idle',
    containerClass: 'bg-muted text-muted-foreground',
    iconClass: 'text-muted-foreground',
    animate: false,
  },
  connecting: {
    icon: Loader2,
    label: 'Connecting...',
    containerClass: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
    iconClass: 'text-amber-600 dark:text-amber-400',
    animate: true,
  },
  connected: {
    icon: CheckCircle2,
    label: 'Connected',
    containerClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
    iconClass: 'text-emerald-600 dark:text-emerald-400',
    animate: false,
  },
  error: {
    icon: XCircle,
    label: 'Error',
    containerClass: 'bg-destructive/10 text-destructive',
    iconClass: 'text-destructive',
    animate: false,
  },
}

/**
 * StatusIndicator - Flow state indicator with animation
 *
 * CONS-13: Flow state indicator shows real-time connection state
 *
 * Visualizes the current connection state with appropriate icon,
 * label, and styling. Connecting and receiving states show animated spinner.
 */
export function StatusIndicator({ state, className }: StatusIndicatorProps) {
  const config = stateConfig[state]
  const Icon = config.icon

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium',
        config.containerClass,
        className
      )}
    >
      <Icon
        className={cn('h-4 w-4', config.iconClass, config.animate && 'animate-spin')}
        aria-label={config.label}
      />
      <span>{config.label}</span>
    </div>
  )
}
