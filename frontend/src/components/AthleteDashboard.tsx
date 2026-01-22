import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Dumbbell, Apple, Calendar, TrendingUp, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import RoutineWizard from './RoutineWizard'
import ApprovalStatusBadge from './ApprovalStatusBadge'
import type { WorkoutPlan, NutritionPlan } from '@/lib/types'

interface AthleteDashboardProps {
  userId: string
}

export default function AthleteDashboard({ userId }: AthleteDashboardProps) {
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null)
  const [nutritionPlan, setNutritionPlan] = useState<NutritionPlan | null>(null)
  const [showWizard, setShowWizard] = useState(false)
  const [loading, setLoading] = useState(false)

  // Removed unused handleGenerateWorkout function
  // Users can click the wizard button directly

  const handleGenerateNutrition = async () => {
    setLoading(true)
    try {
      const plan = await api.generateNutritionPlan(userId)
      setNutritionPlan(plan)
    } catch (error) {
      console.error('Failed to generate nutrition plan:', error)
    } finally {
      setLoading(false)
    }
  }

  if (showWizard) {
    return (
      <RoutineWizard
        userId={userId}
        onComplete={(plan) => {
          setWorkoutPlan(plan)
          setShowWizard(false)
        }}
        onCancel={() => setShowWizard(false)}
      />
    )
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Athlete Dashboard</h1>
            <p className="text-muted-foreground">Manage your fitness journey</p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active Plans</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(workoutPlan?.state === 'active' ? 1 : 0) + (nutritionPlan?.state === 'active' ? 1 : 0)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Workouts</CardTitle>
              <Dumbbell className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{workoutPlan ? '1' : '0'}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Nutrition</CardTitle>
              <Apple className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{nutritionPlan ? '1' : '0'}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Progress</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">--</div>
            </CardContent>
          </Card>
        </div>

        {/* Actions */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Workout Plan</CardTitle>
              <CardDescription>
                {workoutPlan 
                  ? `${workoutPlan.title} - ${workoutPlan.weeks} weeks`
                  : 'Generate your personalized workout plan'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {workoutPlan && (
                <div className="flex items-center gap-2">
                  <ApprovalStatusBadge status={workoutPlan.state} />
                  <span className="text-sm text-muted-foreground">
                    {workoutPlan.days_per_week} days/week
                  </span>
                </div>
              )}
              <div className="flex gap-2">
                <Button 
                  onClick={() => setShowWizard(true)}
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating...</>
                  ) : workoutPlan ? (
                    'Regenerate'
                  ) : (
                    'Generate Plan'
                  )}
                </Button>
                {workoutPlan && workoutPlan.state === 'approved' && (
                  <Button 
                    variant="secondary"
                    onClick={() => api.activateWorkoutPlan(workoutPlan.id, userId)}
                  >
                    Activate
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Nutrition Plan</CardTitle>
              <CardDescription>
                {nutritionPlan 
                  ? `${nutritionPlan.title} - ${nutritionPlan.daily_calories} cal/day`
                  : 'Get your personalized nutrition plan'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {nutritionPlan && (
                <div className="flex items-center gap-2">
                  <ApprovalStatusBadge status={nutritionPlan.state} />
                  <span className="text-sm text-muted-foreground">
                    {nutritionPlan.meals.length} meals/day
                  </span>
                </div>
              )}
              <div className="flex gap-2">
                <Button 
                  onClick={handleGenerateNutrition}
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating...</>
                  ) : nutritionPlan ? (
                    'Regenerate'
                  ) : (
                    'Generate Plan'
                  )}
                </Button>
                {nutritionPlan && nutritionPlan.state === 'approved' && (
                  <Button 
                    variant="secondary"
                    onClick={() => api.activateNutritionPlan(nutritionPlan.id, userId)}
                  >
                    Activate
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Current Workout */}
        {workoutPlan && workoutPlan.state === 'active' && (
          <Card>
            <CardHeader>
              <CardTitle>Current Workout Plan</CardTitle>
              <CardDescription>{workoutPlan.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {workoutPlan.workout_days.map((day, index) => (
                  <div key={index} className="border-l-4 border-primary pl-4">
                    <h4 className="font-semibold">{day.day} - {day.focus}</h4>
                    <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                      {day.exercises.slice(0, 3).map((exercise, i) => (
                        <li key={i}>
                          {exercise.name} - {exercise.sets}x{exercise.reps}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
