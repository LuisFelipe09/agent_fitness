from fastapi import APIRouter, Depends, HTTPException
from src.domain.models import User
from src.application.comment_service import CommentService
from src.application.notification_service import NotificationService
from src.dependencies import (
    get_comment_service,
    get_notification_service
)
from src.interfaces.api.auth import get_current_user
from src.interfaces.api.dto.advanced_dto import CommentCreate

router = APIRouter()

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
