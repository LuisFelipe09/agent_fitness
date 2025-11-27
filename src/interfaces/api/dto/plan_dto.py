"""
Plan-related Data Transfer Objects (DTOs) for API requests.

These DTOs define the structure for plan creation and updates,
keeping API contracts separate from domain models.
"""
from pydantic import BaseModel
from typing import List, Optional

# === Exercise & Workout DTOs ===

class ExerciseRequest(BaseModel):
    """Request model for exercise data"""
    name: str
    description: str
    sets: int
    reps: str
    rest_time: str
    video_url: Optional[str] = None

class WorkoutSessionRequest(BaseModel):
    """Request model for workout session data"""
    day: str
    focus: str
    exercises: List[ExerciseRequest]

class WorkoutPlanUpdateRequest(BaseModel):
    """Request model for updating a workout plan"""
    start_date: str  # ISO format
    end_date: str    # ISO format
    sessions: List[WorkoutSessionRequest]

# === Meal & Nutrition DTOs ===

class MealRequest(BaseModel):
    """Request model for meal data"""
    name: str
    description: str
    calories: int
    protein: int
    carbs: int
    fats: int
    ingredients: List[str]

class DailyMealPlanRequest(BaseModel):
    """Request model for daily meal plan data"""
    day: str
    meals: List[MealRequest]

class NutritionPlanUpdateRequest(BaseModel):
    """Request model for updating a nutrition plan"""
    start_date: str  # ISO format
    end_date: str    # ISO format
    daily_plans: List[DailyMealPlanRequest]
