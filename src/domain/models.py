from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Goal(Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    IMPROVE_ENDURANCE = "improve_endurance"

class ActivityLevel(Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTRA_ACTIVE = "extra_active"

class PlanState(Enum):
    """States for workout and nutrition plans"""
    DRAFT = "draft"           # Created by client or AI, not yet reviewed
    UNDER_REVIEW = "under_review"  # Trainer/nutritionist is reviewing
    APPROVED = "approved"     # Approved by professional, ready to use
    ACTIVE = "active"         # Currently being followed by client
    COMPLETED = "completed"   # Plan period finished

@dataclass
class UserProfile:
    age: int
    weight: float  # in kg
    height: float  # in cm
    gender: str
    goal: Goal
    activity_level: ActivityLevel
    dietary_restrictions: List[str] = field(default_factory=list)
    injuries: List[str] = field(default_factory=list)

@dataclass
class User:
    id: str
    username: str
    roles: List[str] = field(default_factory=lambda: ["client"])  # Store as strings for easy serialization
    profile: Optional[UserProfile] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # Relationships for trainers/nutritionists
    trainer_id: Optional[str] = None
    nutritionist_id: Optional[str] = None
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        from .permissions import Role
        if isinstance(role, Role):
            role = role.value
        return role in self.roles
    
    def has_permission(self, permission) -> bool:
        """Check if user has a specific permission based on their roles"""
        from .permissions import Role, Permission, ROLE_PERMISSIONS
        
        if isinstance(permission, str):
            # Convert string to Permission enum
            try:
                permission = Permission[permission.upper()]
            except KeyError:
                return False
        
        for role_str in self.roles:
            try:
                role = Role(role_str)
                if permission in ROLE_PERMISSIONS.get(role, set()):
                    return True
            except ValueError:
                continue
        return False

@dataclass
class Exercise:
    name: str
    description: str
    sets: int
    reps: str
    rest_time: str  # e.g., "60s"
    video_url: Optional[str] = None

@dataclass
class WorkoutSession:
    day: str  # e.g., "Monday"
    focus: str  # e.g., "Upper Body"
    exercises: List[Exercise]

@dataclass
class WorkoutPlan:
    id: str
    user_id: str
    start_date: datetime
    end_date: datetime
    sessions: List[WorkoutSession]
    created_at: datetime = field(default_factory=datetime.now)
    
    # Traceability fields
    created_by: Optional[str] = None  # User ID who created (client or trainer)
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None  # User ID who last modified (usually trainer)
    
    # State management
    state: str = "draft"  # draft, under_review, approved, active, completed

@dataclass
class Meal:
    name: str
    description: str
    calories: int
    protein: int
    carbs: int
    fats: int
    ingredients: List[str]

@dataclass
class DailyMealPlan:
    day: str
    meals: List[Meal]  # Breakfast, Lunch, Dinner, Snacks

@dataclass
class NutritionPlan:
    id: str
    user_id: str
    start_date: datetime
    end_date: datetime
    daily_plans: List[DailyMealPlan]
    created_at: datetime = field(default_factory=datetime.now)
    
    # Traceability fields
    created_by: Optional[str] = None  # User ID who created (client or nutritionist)
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None  # User ID who last modified (usually nutritionist)
    
    # State management
    state: str = "draft"  # draft, under_review, approved, active, completed
