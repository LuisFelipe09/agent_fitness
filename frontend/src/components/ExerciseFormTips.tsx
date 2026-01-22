import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Lightbulb } from 'lucide-react'

export default function ExerciseFormTips() {
  const tips = [
    {
      exercise: 'Squats',
      tips: [
        'Keep your chest up and core engaged',
        'Knees should track over toes',
        'Go as deep as your mobility allows',
      ]
    },
    {
      exercise: 'Bench Press',
      tips: [
        'Retract your shoulder blades',
        'Keep your feet flat on the ground',
        'Lower the bar to mid-chest',
      ]
    },
    {
      exercise: 'Deadlifts',
      tips: [
        'Keep the bar close to your body',
        'Engage your lats and core',
        'Drive through your heels',
      ]
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          Form Tips
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {tips.map((item, index) => (
          <div key={index}>
            <h4 className="font-semibold text-sm mb-2">{item.exercise}</h4>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {item.tips.map((tip, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
