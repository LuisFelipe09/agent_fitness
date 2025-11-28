from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from src.dependencies import (
    get_role_service,
    get_planning_service,
    get_nutrition_repository,
    get_version_service,
    get_notification_service
)
from src.application.role_service import RoleService
from src.application.planning_service import PlanningService
from src.application.version_service import VersionService
from src.application.notification_service import NotificationService
from src.domain.repositories import NutritionPlanRepository
from src.domain.models import User, DailyMealPlan, Meal, NotificationType
from src.domain.permissions import Role
from src.interfaces.api.auth import get_current_user, require_role
from src.interfaces.api.dto import NutritionPlanUpdateRequest

router = APIRouter()

# ============================================================================
# NUTRITIONIST ENDPOINTS
# ============================================================================

@router.get("/nutritionist/clients", dependencies=[Depends(require_role(Role.NUTRITIONIST))])
def get_my_clients_as_nutritionist(
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """Get all clients assigned to me as their nutritionist"""
    return service.get_my_clients(current_user.id)

@router.post("/nutritionist/clients/{client_id}/assign", dependencies=[Depends(require_role(Role.NUTRITIONIST))])
def assign_myself_as_nutritionist(
    client_id: str,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """Assign myself as nutritionist to a client"""
    try:
        return service.assign_nutritionist(client_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/nutritionist/clients/{client_id}/nutrition-plan", dependencies=[Depends(require_role(Role.NUTRITIONIST))])
def create_nutrition_plan_for_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service),
    role_service: RoleService = Depends(get_role_service)
):
    """Create a nutrition plan for one of my clients"""
    # Verify client is assigned to this nutritionist
    clients = role_service.get_my_clients(current_user.id)
    client_ids = [c.id for c in clients]
    
    if client_id not in client_ids:
        raise HTTPException(
            status_code=403,
            detail="You can only create plans for your assigned clients"
        )
    
    try:
        return service.generate_nutrition_plan(client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/nutritionist/nutrition-plans/{plan_id}", dependencies=[Depends(require_role(Role.NUTRITIONIST))])
def get_nutrition_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    plan_repo: NutritionPlanRepository = Depends(get_nutrition_repository)
):
    """Get a specific nutrition plan to review/edit"""
    # Get the plan
    plan = plan_repo.get_by_id(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")
    
    # Verify this nutritionist is assigned to the client
    clients = role_service.get_my_clients(current_user.id)
    client_ids = [c.id for c in clients]
    
    if plan.user_id not in client_ids:
        raise HTTPException(
            status_code=403,
            detail="You can only view plans for your assigned clients"
        )
    
    return plan

@router.put("/nutritionist/nutrition-plans/{plan_id}", dependencies=[Depends(require_role(Role.NUTRITIONIST))])
def update_nutrition_plan(
    plan_id: str,
    plan_update: NutritionPlanUpdateRequest,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    planning_service: PlanningService = Depends(get_planning_service),
    version_service: VersionService = Depends(get_version_service),
    notif_service: NotificationService = Depends(get_notification_service),
    plan_repo: NutritionPlanRepository = Depends(get_nutrition_repository)
):
    """Update a nutrition plan (nutritionist can modify AI-generated plan)"""
    
    # Get the existing plan
    existing_plan = plan_repo.get_by_id(plan_id)
    
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")
    
    # Verify this nutritionist is assigned to the client
    clients = role_service.get_my_clients(current_user.id)
    client_ids = [c.id for c in clients]
    
    if existing_plan.user_id not in client_ids:
        raise HTTPException(
            status_code=403,
            detail="You can only update plans for your assigned clients"
        )
    
    # Convert Pydantic DTOs to domain models
    daily_plans = []
    for daily_data in plan_update.daily_plans:
        meals = [
            Meal(
                name=meal.name,
                description=meal.description,
                calories=meal.calories,
                protein=meal.protein,
                carbs=meal.carbs,
                fats=meal.fats,
                ingredients=meal.ingredients
            )
            for meal in daily_data.meals
        ]
        daily_plans.append(DailyMealPlan(
            day=daily_data.day,
            meals=meals
        ))
    
    # Create version snapshot before update
    version_service.create_version(
        plan=existing_plan,
        changed_by=current_user.id,
        summary="Nutritionist update: Modified meals"
    )

    # Delegate to service for update
    updated_plan = planning_service.update_nutrition_plan(
        plan_id=plan_id,
        start_date=datetime.fromisoformat(plan_update.start_date),
        end_date=datetime.fromisoformat(plan_update.end_date),
        daily_plans=daily_plans,
        modified_by=current_user.id
    )
    
    # Notify client
    notif_service.create_notification(
        user_id=existing_plan.user_id,
        type=NotificationType.PLAN_UPDATED,
        title="Nutrition Plan Updated",
        message="Your nutritionist has updated your nutrition plan.",
        related_entity_type="nutrition_plan",
        related_entity_id=existing_plan.id
    )
    
    return {"message": "Nutrition plan updated successfully", "plan": updated_plan}
