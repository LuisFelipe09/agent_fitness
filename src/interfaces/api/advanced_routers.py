from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.models import User, PlanVersion, PlanComment, Notification, NotificationType
from src.application.version_service import VersionService
from src.application.comment_service import CommentService
from src.application.notification_service import NotificationService
from src.infrastructure.repositories import (
    SqlAlchemyPlanVersionRepository, 
    SqlAlchemyPlanCommentRepository, 
    SqlAlchemyNotificationRepository,
    SqlAlchemyWorkoutPlanRepository,
    SqlAlchemyNutritionPlanRepository,
    SqlAlchemyUserRepository
)
from src.interfaces.api.auth import get_current_user, require_role
from src.domain.permissions import Role
from src.infrastructure.database import get_db
from pydantic import BaseModel

router = APIRouter()

# Dependency helpers
def get_version_service(db: Session = Depends(get_db)) -> VersionService:
    return VersionService(SqlAlchemyPlanVersionRepository(db))

def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    return CommentService(SqlAlchemyPlanCommentRepository(db))

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(SqlAlchemyNotificationRepository(db))

# Pydantic models
class CommentCreate(BaseModel):
    content: str
    is_internal: bool = False

class CommentResponse(BaseModel):
    id: str
    author_id: str
    author_role: str
    content: str
    created_at: str
    is_internal: bool

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: str
    related_entity_id: Optional[str]

# === VERSION ENDPOINTS ===

@router.get("/plans/{plan_id}/versions")
def get_plan_versions(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: VersionService = Depends(get_version_service),
    db: Session = Depends(get_db)
):
    """Get version history for a plan"""
    # 1. Find the plan to check ownership
    workout_repo = SqlAlchemyWorkoutPlanRepository(db)
    nutrition_repo = SqlAlchemyNutritionPlanRepository(db)
    
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
        user_repo = SqlAlchemyUserRepository(db)
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

# === COMMENT ENDPOINTS ===

@router.post("/plans/{plan_id}/comments")
def add_comment(
    plan_id: str,
    comment: CommentCreate,
    plan_type: str = "workout", # query param
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
    notif_service: NotificationService = Depends(get_notification_service)
):
    """Add a comment to a plan"""
    # Determine role for display
    role = "client"
    if current_user.has_role("trainer"):
        role = "trainer"
    elif current_user.has_role("nutritionist"):
        role = "nutritionist"
    
    # Create comment
    new_comment = service.add_comment(
        plan_id=plan_id,
        plan_type=plan_type,
        author_id=current_user.id,
        author_role=role,
        content=comment.content,
        is_internal=comment.is_internal
    )
    
    # Notify relevant parties (simplified logic)
    # In a real app, we'd look up the plan owner and notify them if they aren't the commenter
    
    return new_comment

@router.get("/plans/{plan_id}/comments")
def get_comments(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    """Get comments for a plan"""
    role = "trainer" if (current_user.has_role("trainer") or current_user.has_role("nutritionist")) else "client"
    return service.get_plan_comments(plan_id, role)

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    """Delete a comment"""
    try:
        service.delete_comment(comment_id, current_user.id)
        return {"message": "Comment deleted"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Cannot delete this comment")

# === NOTIFICATION ENDPOINTS ===

@router.get("/notifications")
def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Get user notifications"""
    return service.get_user_notifications(current_user.id, unread_only)

@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark notification as read"""
    service.mark_as_read(notification_id, current_user.id)
    return {"message": "Marked as read"}

@router.patch("/notifications/mark-all-read")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark all notifications as read"""
    service.mark_all_read(current_user.id)
    return {"message": "All marked as read"}
