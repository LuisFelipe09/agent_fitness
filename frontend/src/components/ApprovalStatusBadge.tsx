import { Badge } from './ui/badge'
import type { PlanState } from '@/lib/types'

interface ApprovalStatusBadgeProps {
  status: PlanState
}

export default function ApprovalStatusBadge({ status }: ApprovalStatusBadgeProps) {
  const variants: Record<PlanState, { variant: 'default' | 'secondary' | 'destructive' | 'outline', label: string }> = {
    draft: { variant: 'outline', label: 'Draft' },
    approved: { variant: 'default', label: 'Approved' },
    active: { variant: 'secondary', label: 'Active' },
    archived: { variant: 'outline', label: 'Archived' },
  }

  const config = variants[status]

  return (
    <Badge variant={config.variant}>
      {config.label}
    </Badge>
  )
}
