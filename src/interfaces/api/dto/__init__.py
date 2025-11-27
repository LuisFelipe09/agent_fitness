"""
Data Transfer Objects (DTOs) for the API layer.

This package contains all Pydantic models used for request/response validation,
separate from domain models to maintain Clean Architecture boundaries.

Structure:
- user_dto: User profile and registration requests
- plan_dto: Workout and nutrition plan requests
- auth_dto: Authentication and role management requests
"""
from .user_dto import UserProfileRequest, UserCreateRequest
from .plan_dto import (
    ExerciseRequest,
    WorkoutSessionRequest,
    WorkoutPlanUpdateRequest,
    MealRequest,
    DailyMealPlanRequest,
    NutritionPlanUpdateRequest
)
from .auth_dto import RoleAssignmentRequest, ProfessionalAssignmentRequest

__all__ = [
    # User DTOs
    "UserProfileRequest",
    "UserCreateRequest",
    # Plan DTOs
    "ExerciseRequest",
    "WorkoutSessionRequest",
    "WorkoutPlanUpdateRequest",
    "MealRequest",
    "DailyMealPlanRequest",
    "NutritionPlanUpdateRequest",
    # Auth DTOs
    "RoleAssignmentRequest",
    "ProfessionalAssignmentRequest",
]
