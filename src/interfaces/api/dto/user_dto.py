"""
User-related Data Transfer Objects (DTOs) for API requests and responses.

These DTOs serve as the contract between the API layer and clients,
separate from domain models to follow Clean Architecture principles.
"""
from pydantic import BaseModel
from typing import List

class UserProfileRequest(BaseModel):
    """Request model for creating or updating a user profile"""
    age: int
    weight: float
    height: float
    gender: str
    goal: str  # "muscle_gain", "weight_loss", "maintenance"
    activity_level: str  # "sedentary", "light", "moderate", "active", "very_active"
    dietary_restrictions: List[str] = []
    injuries: List[str] = []

class UserCreateRequest(BaseModel):
    """Request model for user registration"""
    id: str
    username: str
