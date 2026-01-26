import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Textarea } from './ui/textarea'
import { Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api'
import type { WorkoutPlan, RoutineForm, UserProfile, ActivityLevel, Goal } from '@/lib/types'

interface RoutineWizardProps {
  userId: string
  onComplete: (plan: WorkoutPlan) => void
  onCancel: () => void
}

// Injury-related keywords for parsing preferences
const INJURY_KEYWORDS = ['injury', 'injured', 'pain', 'hurt', 'surgery', 'limitation', 'issue', 'problem']

export default function RoutineWizard({ userId, onComplete, onCancel }: RoutineWizardProps) {
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [form, setForm] = useState<RoutineForm>({
    age: 25,
    weight: 70,
    height: 170,
    gender: 'male',
    goal: 'muscle_gain',
    experienceLevel: 'intermediate',
    daysPerWeek: 4,
    duration: 12,
    equipment: [],
    preferences: ''
  })

  // Fetch existing user profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const userData = await api.getMe(userId)
        setProfile(userData.profile || null)
        
        // Pre-fill form with existing profile data if available
        if (userData.profile) {
          setForm(prev => ({
            ...prev,
            age: userData.profile.age || prev.age,
            weight: userData.profile.weight || prev.weight,
            height: userData.profile.height || prev.height,
            gender: userData.profile.gender || prev.gender
          }))
        }
      } catch (error) {
        console.error('Failed to fetch user profile:', error)
      }
    }
    fetchProfile()
  }, [userId])

  const handleNext = () => setStep(step + 1)
  const handleBack = () => setStep(step - 1)

  // Map experience level to activity level
  const mapExperienceLevelToActivityLevel = (experienceLevel: string): ActivityLevel => {
    const mapping: Record<string, ActivityLevel> = {
      'beginner': 'sedentary',
      'intermediate': 'moderately_active',
      'advanced': 'very_active'
    }
    return mapping[experienceLevel] || 'moderately_active'
  }

  // Parse injuries from preferences text field
  const parseInjuriesFromPreferences = (preferences: string): string[] => {
    if (!preferences.trim()) return []
    
    const lines = preferences.toLowerCase().split(/[.,;:\n]/).filter(line => line.trim())
    
    const injuries: string[] = []
    for (const line of lines) {
      if (INJURY_KEYWORDS.some(keyword => line.includes(keyword))) {
        injuries.push(line.trim())
      }
    }
    
    return injuries
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      // 1. Update user profile with wizard data
      const profileUpdate: UserProfile = {
        goal: form.goal as Goal,
        activity_level: mapExperienceLevelToActivityLevel(form.experienceLevel),
        injuries: parseInjuriesFromPreferences(form.preferences || ''),
        // Use user-provided profile data from form
        age: form.age,
        weight: form.weight,
        height: form.height,
        gender: form.gender,
        dietary_restrictions: profile?.dietary_restrictions || []
      }
      
      await api.updateProfile(userId, profileUpdate)
      
      // 2. Generate plan with updated profile
      const plan = await api.generateWorkoutPlan(userId)
      onComplete(plan)
    } catch (error) {
      console.error('Failed to generate plan:', error)
      // TODO: Show error toast to user
    } finally {
      setLoading(false)
    }
  }

  const updateForm = (field: keyof RoutineForm, value: any) => {
    setForm({ ...form, [field]: value })
  }

  // Validation for Step 1 (Basic Profile)
  const canProceedFromStep1 = () => {
    return form.age >= 13 && form.age <= 100 &&
           form.weight >= 30 && form.weight <= 200 &&
           form.height >= 100 && form.height <= 250 &&
           (form.gender === 'male' || form.gender === 'female' || form.gender === 'other')
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8 flex items-center justify-center">
      <Card className="max-w-2xl w-full">
        <CardHeader>
          <CardTitle>Create Your Workout Plan</CardTitle>
          <CardDescription>Step {step} of 4 - Let's personalize your routine</CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {step === 1 && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Age</label>
                  <Input
                    type="number"
                    min="13"
                    max="100"
                    value={form.age}
                    onChange={(e) => updateForm('age', parseInt(e.target.value) || 0)}
                    placeholder="25"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Gender</label>
                  <select
                    className="w-full p-2 border rounded-md bg-background"
                    value={form.gender}
                    onChange={(e) => updateForm('gender', e.target.value)}
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Weight (kg)</label>
                  <Input
                    type="number"
                    min="30"
                    max="200"
                    step="0.1"
                    value={form.weight}
                    onChange={(e) => updateForm('weight', parseFloat(e.target.value) || 0)}
                    placeholder="70"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Height (cm)</label>
                  <Input
                    type="number"
                    min="100"
                    max="250"
                    value={form.height}
                    onChange={(e) => updateForm('height', parseInt(e.target.value) || 0)}
                    placeholder="170"
                  />
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">What's your primary goal?</label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'muscle_gain', label: 'Build Muscle' },
                    { value: 'weight_loss', label: 'Lose Weight' },
                    { value: 'improve_endurance', label: 'Improve Endurance' },
                    { value: 'maintenance', label: 'Stay Fit' },
                  ].map((option) => (
                    <Button
                      key={option.value}
                      variant={form.goal === option.value ? 'default' : 'outline'}
                      onClick={() => updateForm('goal', option.value)}
                      className="h-auto py-3"
                    >
                      {option.label}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Experience Level</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'beginner', label: 'Beginner' },
                    { value: 'intermediate', label: 'Intermediate' },
                    { value: 'advanced', label: 'Advanced' },
                  ].map((option) => (
                    <Button
                      key={option.value}
                      variant={form.experienceLevel === option.value ? 'default' : 'outline'}
                      onClick={() => updateForm('experienceLevel', option.value)}
                    >
                      {option.label}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Days per week: {form.daysPerWeek}
                </label>
                <Input
                  type="range"
                  min="2"
                  max="7"
                  value={form.daysPerWeek}
                  onChange={(e) => updateForm('daysPerWeek', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>2 days</span>
                  <span>7 days</span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Program duration: {form.duration} weeks
                </label>
                <Input
                  type="range"
                  min="4"
                  max="16"
                  step="2"
                  value={form.duration}
                  onChange={(e) => updateForm('duration', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>4 weeks</span>
                  <span>16 weeks</span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Available Equipment</label>
                <div className="grid grid-cols-2 gap-2">
                  {['Dumbbells', 'Barbell', 'Resistance Bands', 'Pull-up Bar', 'Bench', 'Bodyweight Only'].map((equipment) => (
                    <Button
                      key={equipment}
                      variant={form.equipment.includes(equipment) ? 'default' : 'outline'}
                      onClick={() => {
                        const current = form.equipment
                        updateForm(
                          'equipment',
                          current.includes(equipment)
                            ? current.filter((e) => e !== equipment)
                            : [...current, equipment]
                        )
                      }}
                      size="sm"
                    >
                      {equipment}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Additional Preferences (Optional)
                </label>
                <Textarea
                  placeholder="Any injuries, favorite exercises, time constraints, etc."
                  value={form.preferences}
                  onChange={(e) => updateForm('preferences', e.target.value)}
                  rows={6}
                />
              </div>

              <div className="bg-muted p-4 rounded-lg space-y-2 text-sm">
                <h4 className="font-semibold">Your Plan Summary:</h4>
                <ul className="space-y-1 text-muted-foreground">
                  <li>• Goal: {form.goal.replace('_', ' ')}</li>
                  <li>• Level: {form.experienceLevel}</li>
                  <li>• Frequency: {form.daysPerWeek} days/week</li>
                  <li>• Duration: {form.duration} weeks</li>
                  <li>• Equipment: {form.equipment.length > 0 ? form.equipment.join(', ') : 'None selected'}</li>
                </ul>
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={step === 1 ? onCancel : handleBack}>
            <ChevronLeft className="mr-2 h-4 w-4" />
            {step === 1 ? 'Cancel' : 'Back'}
          </Button>

          {step < 4 ? (
            <Button onClick={handleNext} disabled={step === 1 && !canProceedFromStep1()}>
              Next
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                'Generate Plan'
              )}
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  )
}
