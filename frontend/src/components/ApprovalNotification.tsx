import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { CheckCircle2, XCircle } from 'lucide-react'

interface ApprovalNotificationProps {
  title: string
  message: string
  approved: boolean
  onDismiss: () => void
}

export default function ApprovalNotification({ 
  title, 
  message, 
  approved, 
  onDismiss 
}: ApprovalNotificationProps) {
  return (
    <Card className={`border-l-4 ${approved ? 'border-l-green-500' : 'border-l-red-500'}`}>
      <CardHeader>
        <div className="flex items-start gap-3">
          {approved ? (
            <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
          ) : (
            <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
          )}
          <div className="flex-1">
            <CardTitle className="text-base">{title}</CardTitle>
            <CardDescription className="mt-1">{message}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Button variant="outline" size="sm" onClick={onDismiss}>
          Dismiss
        </Button>
      </CardContent>
    </Card>
  )
}
