import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Textarea } from './ui/textarea'
import { CheckCircle, XCircle } from 'lucide-react'
import type { WorkoutPlan } from '@/lib/types'

interface RoutineReviewPanelProps {
  plan: WorkoutPlan
  onApprove: (feedback: string) => void
  onReject: (feedback: string) => void
}

export default function RoutineReviewPanel({ plan, onApprove, onReject }: RoutineReviewPanelProps) {
  const [feedback, setFeedback] = useState('')

  return (
    <Card>
      <CardHeader>
        <CardTitle>Review Workout Plan</CardTitle>
        <CardDescription>
          Athlete: {plan.user_id} • Created: {new Date(plan.created_at).toLocaleDateString()}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="font-semibold mb-2">{plan.title}</h3>
          <p className="text-sm text-muted-foreground">{plan.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Duration:</span>
            <span className="ml-2 font-medium">{plan.weeks} weeks</span>
          </div>
          <div>
            <span className="text-muted-foreground">Frequency:</span>
            <span className="ml-2 font-medium">{plan.days_per_week} days/week</span>
          </div>
        </div>

        <div className="space-y-3">
          <h4 className="font-semibold text-sm">Workout Schedule:</h4>
          {plan.workout_days.map((day, index) => (
            <div key={index} className="border rounded-lg p-3">
              <h5 className="font-medium">{day.day} - {day.focus}</h5>
              <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                {day.exercises.map((exercise, i) => (
                  <li key={i}>
                    {exercise.name} - {exercise.sets}x{exercise.reps} ({exercise.rest} rest)
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Review Feedback</label>
          <Textarea
            placeholder="Add your feedback or suggestions..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={4}
          />
        </div>

        <div className="flex gap-3">
          <Button
            variant="destructive"
            className="flex-1"
            onClick={() => onReject(feedback)}
          >
            <XCircle className="mr-2 h-4 w-4" />
            Request Changes
          </Button>
          <Button
            className="flex-1"
            onClick={() => onApprove(feedback)}
          >
            <CheckCircle className="mr-2 h-4 w-4" />
            Approve Plan
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
