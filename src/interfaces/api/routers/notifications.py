from fastapi import APIRouter, Depends
from src.domain.models import User
from src.application.notification_service import NotificationService
from src.dependencies import get_notification_service
from src.interfaces.api.auth import get_current_user

router = APIRouter()

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
