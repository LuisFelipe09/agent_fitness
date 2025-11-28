from fastapi import APIRouter, Depends, HTTPException
from src.domain.models import User
from src.domain.repositories import (
    WorkoutPlanRepository,
    NutritionPlanRepository,
    UserRepository
)
from src.application.version_service import VersionService
from src.dependencies import (
    get_version_service,
    get_workout_repository,
    get_nutrition_repository,
    get_user_repository
)
from src.interfaces.api.auth import get_current_user

router = APIRouter()

# === VERSION ENDPOINTS ===

@router.get("/plans/{plan_id}/versions")
def get_plan_versions(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: VersionService = Depends(get_version_service),
    workout_repo: WorkoutPlanRepository = Depends(get_workout_repository),
    nutrition_repo: NutritionPlanRepository = Depends(get_nutrition_repository),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get version history for a plan"""
    # 1. Find the plan to check ownership
    plan = workout_repo.get_by_id(plan_id)
    if not plan:
        plan = nutrition_repo.get_by_id(plan_id)
        
    if not plan:
        # If plan doesn't exist, maybe it was deleted but versions remain?
        # For security, we shouldn't show versions if we can't verify ownership.
        raise HTTPException(status_code=404, detail="Plan not found")

    # 2. Check permissions
    if plan.user_id != current_user.id:
        # Not the owner. Check if authorized professional.
        plan_owner = user_repo.get_by_id(plan.user_id)
        
        if not plan_owner:
             raise HTTPException(status_code=404, detail="Plan owner not found")

        is_authorized = False
        
        # Admin always has access
        if current_user.has_role("admin"):
            is_authorized = True
            
        # Trainer check
        elif current_user.has_role("trainer"):
            if plan_owner.trainer_id == current_user.id:
                is_authorized = True
                
        # Nutritionist check
        elif current_user.has_role("nutritionist"):
            if plan_owner.nutritionist_id == current_user.id:
                is_authorized = True
        
        if not is_authorized:
            raise HTTPException(status_code=403, detail="Not authorized to view this plan's history")

    versions = service.get_history(plan_id)
    return versions
