from fastapi import APIRouter, Depends, HTTPException
from src.dependencies import (
    get_user_service,
    get_user_repository,
)
from src.application.user_service import UserService
from src.domain.repositories import UserRepository
from src.domain.models import User, UserProfile, Goal, ActivityLevel
from src.interfaces.api.auth import get_current_user
from src.interfaces.api.dto import UserCreateRequest, UserProfileRequest

router = APIRouter()

# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@router.post("/users/")
def create_user(user: UserCreateRequest, service: UserService = Depends(get_user_service)):
    """Register a new user (called by Telegram bot)"""
    return service.register_user(user.id, user.username)

# ============================================================================
# USER PROFILE ENDPOINTS
# ============================================================================

@router.get("/users/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@router.put("/users/me/profile")
def update_my_profile(
    profile: UserProfileRequest, 
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Update current user's profile"""
    try:
        domain_profile = UserProfile(
            age=profile.age,
            weight=profile.weight,
            height=profile.height,
            gender=profile.gender,
            goal=Goal(profile.goal),
            activity_level=ActivityLevel(profile.activity_level),
            dietary_restrictions=profile.dietary_restrictions,
            injuries=profile.injuries
        )
        return service.update_profile(current_user.id, domain_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/me/trainer")
def get_my_trainer(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get my assigned trainer"""
    if not current_user.trainer_id:
        return {"trainer": None, "message": "No trainer assigned"}
    
    trainer = user_repo.get_by_id(current_user.trainer_id)
    return {"trainer": trainer}

@router.get("/users/me/nutritionist")
def get_my_nutritionist(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get my assigned nutritionist"""
    if not current_user.nutritionist_id:
        return {"nutritionist": None, "message": "No nutritionist assigned"}
    
    nutritionist = user_repo.get_by_id(current_user.nutritionist_id)
    return {"nutritionist": nutritionist}
