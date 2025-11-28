from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from src.dependencies import (
    get_role_service,
    get_planning_service,
    get_workout_repository,
    get_version_service,
    get_notification_service
)
from src.application.role_service import RoleService
from src.application.planning_service import PlanningService
from src.application.version_service import VersionService
from src.application.notification_service import NotificationService
from src.domain.repositories import WorkoutPlanRepository
from src.domain.models import User, WorkoutSession, Exercise, NotificationType
from src.domain.permissions import Role
from src.interfaces.api.auth import get_current_user, require_role
from src.interfaces.api.dto import WorkoutPlanUpdateRequest

router = APIRouter()

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
