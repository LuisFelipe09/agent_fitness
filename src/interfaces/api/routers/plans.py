from fastapi import APIRouter, Depends, HTTPException
from src.dependencies import (
    get_planning_service,
    get_workout_repository,
    get_nutrition_repository
)
from src.application.planning_service import PlanningService
from src.domain.repositories import WorkoutPlanRepository, NutritionPlanRepository
from src.domain.models import User
from src.interfaces.api.auth import get_current_user

router = APIRouter()

# ============================================================================
# PLAN GENERATION ENDPOINTS
# ============================================================================

@router.post("/plans/workout")
def generate_my_workout(
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service)
):
    """Generate workout plan for current user"""
    try:
        return service.generate_workout_plan(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/plans/nutrition")
def generate_my_nutrition(
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service)
):
    try:
        return service.generate_nutrition_plan(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/plans/workout/current")
def get_my_current_workout_plan(
    current_user: User = Depends(get_current_user),
    plan_repo: WorkoutPlanRepository = Depends(get_workout_repository)
):
    """Get the current workout plan for the logged-in user"""
    plan = plan_repo.get_current_plan(current_user.id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="No active workout plan found")
        
    return plan

@router.post("/plans/workout/{plan_id}/activate")
def activate_my_workout_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service)
):
    """Activate a workout plan"""
    try:
        return service.activate_workout_plan(plan_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/plans/nutrition/current")
def get_my_current_nutrition_plan(
    current_user: User = Depends(get_current_user),
    plan_repo: NutritionPlanRepository = Depends(get_nutrition_repository)
):
    """Get the current nutrition plan for the logged-in user"""
    plan = plan_repo.get_current_plan(current_user.id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="No active nutrition plan found")
        
    return plan

@router.post("/plans/nutrition/{plan_id}/activate")
def activate_my_nutrition_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service)
):
    """Activate a nutrition plan"""
    try:
        return service.activate_nutrition_plan(plan_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
