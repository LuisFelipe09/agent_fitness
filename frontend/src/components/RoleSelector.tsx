import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { User, Users } from 'lucide-react'

interface RoleSelectorProps {
  onRoleSelect: (role: 'athlete' | 'coach') => void
}

export default function RoleSelector({ onRoleSelect }: RoleSelectorProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Choose Your Role</h1>
          <p className="text-muted-foreground">
            Select how you want to use the AI Fitness Agent
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <div className="rounded-full bg-primary p-4">
                  <User className="h-8 w-8 text-primary-foreground" />
                </div>
              </div>
              <CardTitle className="text-center">Athlete</CardTitle>
              <CardDescription className="text-center">
                Get personalized workout and nutrition plans
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Generate AI-powered workout routines</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Get custom nutrition plans</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Track your progress</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Receive coach feedback</span>
                </li>
              </ul>
              <Button 
                className="w-full mt-4" 
                onClick={() => onRoleSelect('athlete')}
              >
                Continue as Athlete
              </Button>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <div className="rounded-full bg-secondary p-4">
                  <Users className="h-8 w-8 text-secondary-foreground" />
                </div>
              </div>
              <CardTitle className="text-center">Coach</CardTitle>
              <CardDescription className="text-center">
                Review and manage athlete plans
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-secondary">•</span>
                  <span>Review AI-generated plans</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-secondary">•</span>
                  <span>Approve or request changes</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-secondary">•</span>
                  <span>Manage multiple athletes</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-secondary">•</span>
                  <span>Provide expert feedback</span>
                </li>
              </ul>
              <Button 
                className="w-full mt-4" 
                variant="secondary"
                onClick={() => onRoleSelect('coach')}
              >
                Continue as Coach
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
