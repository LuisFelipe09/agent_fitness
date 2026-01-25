import { Card, CardContent } from './ui/card'
import { Button } from './ui/button'
import { Dumbbell } from 'lucide-react'

interface WelcomeScreenProps {
  onComplete: () => void
}

export default function WelcomeScreen({ onComplete }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <Card className="max-w-md w-full">
        <CardContent className="pt-6 text-center space-y-6">
          <div className="flex justify-center">
            <div className="rounded-full bg-primary p-4">
              <Dumbbell className="h-12 w-12 text-primary-foreground" />
            </div>
          </div>
          
          <div className="space-y-2">
            <h1 className="text-3xl font-bold">AI Fitness Agent</h1>
            <p className="text-muted-foreground">
              Your intelligent workout and nutrition planning assistant
            </p>
          </div>

          <div className="space-y-3 text-sm text-left">
            <div className="flex items-start gap-3">
              <span className="text-primary">✓</span>
              <span>AI-powered personalized workout plans</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-primary">✓</span>
              <span>Custom nutrition plans based on your goals</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-primary">✓</span>
              <span>Professional coach review and approval</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-primary">✓</span>
              <span>Track progress and adjust plans</span>
            </div>
          </div>

          <Button onClick={onComplete} className="w-full" size="lg">
            Get Started
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
