// Type definitions matching backend Pydantic models

export type UserRole = 'admin' | 'trainer' | 'nutritionist' | 'client'

export type PlanState = 'draft' | 'approved' | 'active' | 'archived'

export type Gender = 'male' | 'female' | 'other'

export type Goal = 'weight_loss' | 'muscle_gain' | 'maintenance' | 'improve_endurance'

export type ActivityLevel = 'sedentary' | 'lightly_active' | 'moderately_active' | 'very_active' | 'extra_active'

export interface UserProfile {
  age?: number
  weight?: number
  height?: number
  gender?: Gender
  goal?: Goal
  activity_level?: ActivityLevel
  dietary_restrictions?: string[]
  medical_conditions?: string[]
  injuries?: string[]
}

export interface User {
  id: string
  telegram_id?: string
  username: string
  email?: string
  role: UserRole
  profile?: UserProfile
  created_at: string
}

export interface Exercise {
  name: string
  sets: number
  reps: string
  rest: string
  notes?: string
}

export interface WorkoutDay {
  day: string
  focus: string
  exercises: Exercise[]
}

export interface WorkoutPlan {
  id: string
  user_id: string
  title: string
  description: string
  weeks: number
  days_per_week: number
  workout_days: WorkoutDay[]
  state: PlanState
  created_at: string
  updated_at?: string
  created_by?: string
  approved_by?: string
  approved_at?: string
  // Plan context - what this plan was designed for
  goal?: Goal
  target_activity_level?: ActivityLevel
}

export interface Meal {
  name: string
  time: string
  foods: string[]
  calories: number
  protein: number
  carbs: number
  fats: number
}

export interface NutritionPlan {
  id: string
  user_id: string
  title: string
  description: string
  daily_calories: number
  protein_grams: number
  carbs_grams: number
  fats_grams: number
  meals: Meal[]
  state: PlanState
  created_at: string
  updated_at?: string
  created_by?: string
  approved_by?: string
  approved_at?: string
  // Plan context - what this plan was designed for
  goal?: Goal
  target_activity_level?: ActivityLevel
}

export interface Notification {
  id: string
  user_id: string
  title: string
  message: string
  type: string
  is_read: boolean
  created_at: string
}

export interface Comment {
  id: string
  plan_id: string
  plan_type: 'workout' | 'nutrition'
  user_id: string
  content: string
  created_at: string
  user_name?: string
}

export interface PlanVersion {
  id: string
  plan_id: string
  plan_type: 'workout' | 'nutrition'
  version_number: number
  data: any
  created_by: string
  created_at: string
  change_notes?: string
}

// Frontend-specific types
export interface RoutineForm {
  // Profile fields
  age: number
  weight: number
  height: number
  gender: Gender
  // Workout preferences
  goal: string
  experienceLevel: 'beginner' | 'intermediate' | 'advanced'
  daysPerWeek: number
  duration: number
  equipment: string[]
  preferences?: string
}
