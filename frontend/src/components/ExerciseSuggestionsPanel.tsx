import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Sparkles } from 'lucide-react'

interface Exercise {
  name: string
  muscleGroups: string[]
  difficulty: 'beginner' | 'intermediate' | 'advanced'
}

export default function ExerciseSuggestionsPanel() {
  const suggestions: Exercise[] = [
    {
      name: 'Bulgarian Split Squats',
      muscleGroups: ['Quads', 'Glutes'],
      difficulty: 'intermediate'
    },
    {
      name: 'Face Pulls',
      muscleGroups: ['Rear Delts', 'Upper Back'],
      difficulty: 'beginner'
    },
    {
      name: 'Romanian Deadlifts',
      muscleGroups: ['Hamstrings', 'Lower Back'],
      difficulty: 'intermediate'
    },
    {
      name: 'Cable Lateral Raises',
      muscleGroups: ['Side Delts'],
      difficulty: 'beginner'
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          AI Exercise Suggestions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {suggestions.map((exercise, index) => (
            <div key={index} className="border rounded-lg p-3 hover:border-primary transition-colors cursor-pointer">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium">{exercise.name}</h4>
                <Badge variant="outline" className="text-xs">
                  {exercise.difficulty}
                </Badge>
              </div>
              <div className="flex gap-2 flex-wrap">
                {exercise.muscleGroups.map((muscle, i) => (
                  <span key={i} className="text-xs bg-muted px-2 py-1 rounded">
                    {muscle}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
