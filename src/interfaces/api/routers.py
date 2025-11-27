from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from src.dependencies import (
    get_user_service,
    get_planning_service,
    get_role_service,
    get_user_repository,
    get_workout_repository,
    get_nutrition_repository,
    get_version_service,
    get_notification_service
)
from src.application.user_service import UserService
from src.application.planning_service import PlanningService
from src.application.role_service import RoleService
from src.application.version_service import VersionService
from src.application.notification_service import NotificationService
from src.domain.repositories import (
    UserRepository,
    WorkoutPlanRepository,
    NutritionPlanRepository
)
from src.domain.models import (
    UserProfile, Goal, ActivityLevel, User,
    NotificationType
)
from src.domain.permissions import Role
from src.interfaces.api.auth import (
    get_current_user,
    require_role
)
from src.interfaces.api.dto import (
    UserProfileRequest,
    UserCreateRequest,
    RoleAssignmentRequest,
    ProfessionalAssignmentRequest,
    WorkoutPlanUpdateRequest,
    NutritionPlanUpdateRequest
)

router = APIRouter()


# ============================================================================
# PUBLIC ENDPOINTS (No authentication required for initial registration)
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
    """Generate nutrition plan for current user"""
    try:
        return service.generate_nutrition_plan(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.get("/admin/users", dependencies=[Depends(require_role(Role.ADMIN))])
def list_all_users(
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """List all users in the system (admin only)"""
    return service.get_all_users(current_user.id)

@router.get("/admin/users/role/{role}", dependencies=[Depends(require_role(Role.ADMIN))])
def list_users_by_role(
    role: str,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """List all users with a specific role (admin only)"""
    try:
        return service.get_users_by_role(current_user.id, role)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/admin/users/{user_id}/roles", dependencies=[Depends(require_role(Role.ADMIN))])
def assign_role_to_user(
    user_id: str,
    role_data: RoleAssignmentRequest,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """Assign a role to a user (admin only)"""
    try:
        return service.assign_role(current_user.id, user_id, role_data.role)
    except (PermissionError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/admin/users/{user_id}/roles/{role}", dependencies=[Depends(require_role(Role.ADMIN))])
def remove_role_from_user(
    user_id: str,
    role: str,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """Remove a role from a user (admin only)"""
    try:
        return service.remove_role(current_user.id, user_id, role)
    except (PermissionError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# TRAINER ENDPOINTS
# ============================================================================

@router.get("/trainer/clients", dependencies=[Depends(require_role(Role.TRAINER))])
def get_my_clients_as_trainer(
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """Get all clients assigned to me as their trainer"""
    return service.get_my_clients(current_user.id)

@router.post("/trainer/clients/{client_id}/assign", dependencies=[Depends(require_role(Role.TRAINER))])
def assign_myself_as_trainer(
    client_id: str,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """Assign myself as trainer to a client"""
    try:
        return service.assign_trainer(client_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trainer/clients/{client_id}/workout-plan", dependencies=[Depends(require_role(Role.TRAINER))])
def create_workout_plan_for_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service),
    role_service: RoleService = Depends(get_role_service)
):
    """Create a workout plan for one of my clients"""
    # Verify client is assigned to this trainer
    clients = role_service.get_my_clients(current_user.id)
    client_ids = [c.id for c in clients]
    
    if client_id not in client_ids:
        raise HTTPException(
            status_code=403, 
            detail="You can only create plans for your assigned clients"
        )
    
    try:
        return service.generate_workout_plan(client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trainer/workout-plans/{plan_id}", dependencies=[Depends(require_role(Role.TRAINER))])
def get_workout_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    plan_repo: WorkoutPlanRepository = Depends(get_workout_repository)
):
    """Get a specific workout plan to review/edit"""
    # Get the latest plan
    plan = plan_repo.get_current_plan(current_user.id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Verify this trainer is assigned to the client
    clients = role_service.get_my_clients(current_user.id)
    client_ids = [c.id for c in clients]
    
    if plan.user_id not in client_ids:
        raise HTTPException(
            status_code=403,
            detail="You can only view plans for your assigned clients"
        )
    
    return plan

@router.put("/trainer/workout-plans/{plan_id}", dependencies=[Depends(require_role(Role.TRAINER))])
def update_workout_plan(
    plan_id: str,
    plan_update: WorkoutPlanUpdateRequest,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    planning_service: PlanningService = Depends(get_planning_service),
    version_service: VersionService = Depends(get_version_service),
    notif_service: NotificationService = Depends(get_notification_service),
    plan_repo: WorkoutPlanRepository = Depends(get_workout_repository)
):
    """Update a workout plan (trainer can modify AI-generated plan)"""
    from datetime import datetime
    from src.domain.models import WorkoutSession, Exercise
    
    # Get the existing plan
    existing_plan = plan_repo.get_by_id(plan_id)
    
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    # Verify this trainer is assigned to the client
    clients = role_service.get_my_clients(current_user.id)
    client_ids = [c.id for c in clients]
    
    if existing_plan.user_id not in client_ids:
        raise HTTPException(
            status_code=403,
            detail="You can only update plans for your assigned clients"
        )
    
    # Convert Pydantic DTOs to domain models
    sessions = []
    for session_data in plan_update.sessions:
        exercises = [
            Exercise(
                name=ex.name,
                description=ex.description,
                sets=ex.sets,
                reps=ex.reps,
                rest_time=ex.rest_time,
                video_url=ex.video_url
            )
            for ex in session_data.exercises
        ]
        sessions.append(WorkoutSession(
            day=session_data.day,
            focus=session_data.focus,
            exercises=exercises
        ))
    
    # Create version snapshot before update
    version_service.create_version(
        plan=existing_plan,
        changed_by=current_user.id,
        summary="Trainer update: Modified sessions/exercises"
    )
    
    # Delegate to service for update
    updated_plan = planning_service.update_workout_plan(
        plan_id=plan_id,
        start_date=datetime.fromisoformat(plan_update.start_date),
        end_date=datetime.fromisoformat(plan_update.end_date),
        sessions=sessions,
        modified_by=current_user.id
    )
    
    # Notify client
    notif_service.create_notification(
        user_id=existing_plan.user_id,
        type=NotificationType.PLAN_UPDATED,
        title="Workout Plan Updated",
        message="Your trainer has updated your workout plan.",
        related_entity_type="workout_plan",
        related_entity_id=existing_plan.id
    )
    
    return {"message": "Workout plan updated successfully", "plan": updated_plan}


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
    from datetime import datetime
    from src.domain.models import DailyMealPlan, Meal
    
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


# ============================================================================
# LEGACY ENDPOINTS (Deprecated - kept for backward compatibility)
# ============================================================================

@router.put("/users/{user_id}/profile")
def update_profile(user_id: str, profile: UserProfileRequest, service: UserService = Depends(get_user_service)):
    """DEPRECATED: Use /users/me/profile instead"""
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
        return service.update_profile(user_id, domain_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}/plans/workout/current")
def get_current_workout_plan(
    user_id: str,
    current_user: User = Depends(get_current_user),
    plan_repo: WorkoutPlanRepository = Depends(get_workout_repository)
):
    """Get the current workout plan for a user"""
    # Authorization: User can see their own plan, or their trainer can see it
    if current_user.id != user_id:
        # Check if trainer
        # Simplified check: if user has trainer role, we assume they might be the trainer
        # Real check should verify relationship
        if not (current_user.has_role("trainer") or current_user.has_role("admin")):
             raise HTTPException(status_code=403, detail="Not authorized to view this plan")

    plan = plan_repo.get_current_plan(user_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="No active workout plan found")
        
    return plan

@router.post("/users/{user_id}/plans/workout/{plan_id}/activate")
def activate_workout_plan(
    user_id: str,
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service)
):
    """Activate a workout plan (Client only)"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to activate this plan")
        
    try:
        return service.activate_workout_plan(plan_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/{user_id}/plans/workout")
def generate_workout(user_id: str, service: PlanningService = Depends(get_planning_service)):
    """DEPRECATED: Use /plans/workout instead"""
    try:
        return service.generate_workout_plan(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}/plans/nutrition/current")
def get_current_nutrition_plan(
    user_id: str,
    current_user: User = Depends(get_current_user),
    plan_repo: NutritionPlanRepository = Depends(get_nutrition_repository)
):
    """Get the current nutrition plan for a user"""
    if current_user.id != user_id:
        if not (current_user.has_role("nutritionist") or current_user.has_role("admin")):
             raise HTTPException(status_code=403, detail="Not authorized to view this plan")

    plan = plan_repo.get_current_plan(user_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="No active nutrition plan found")
        
    return plan

@router.post("/users/{user_id}/plans/nutrition/{plan_id}/activate")
def activate_nutrition_plan(
    user_id: str,
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service)
):
    """Activate a nutrition plan (Client only)"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to activate this plan")
        
    try:
        return service.activate_nutrition_plan(plan_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/{user_id}/plans/nutrition")
def generate_nutrition(user_id: str, service: PlanningService = Depends(get_planning_service)):
    """DEPRECATED: Use /plans/nutrition instead"""
    try:
        return service.generate_nutrition_plan(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
