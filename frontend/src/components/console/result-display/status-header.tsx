import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { AgentResult } from '@/lib/stores/slices/console'

export interface StatusHeaderProps {
  result: AgentResult | null
}

/**
 * StatusHeader displays the traceId and status badge for execution results
 */
export function StatusHeader({ result }: StatusHeaderProps) {
  const status = result?.success ? 'success' : result ? 'failed' : 'idle'

  const badgeVariant = status === 'success' ? 'default' : status === 'failed' ? 'destructive' : 'outline'

  return (
    <div className="flex items-center gap-3">
      <Badge variant={badgeVariant}>{status}</Badge>
      <span className={cn('font-mono text-sm text-muted-foreground')}>
        {result?.traceId || '-'}
      </span>
    </div>
  )
}
