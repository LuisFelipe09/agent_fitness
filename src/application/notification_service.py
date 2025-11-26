from datetime import datetime
from typing import List, Optional
import uuid
from src.domain.models import Notification, NotificationType
from src.domain.repositories import NotificationRepository

class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo
    
    def create_notification(self, user_id: str, type: NotificationType, title: str, message: str, related_entity_type: str = None, related_entity_id: str = None) -> Notification:
        """Create and save a notification"""
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=type.value if hasattr(type, 'value') else type,
            title=title,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            is_read=False,
            created_at=datetime.now()
        )
        self.notification_repo.save(notification)
        return notification
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user"""
        return self.notification_repo.get_by_user_id(user_id, unread_only)
    
    def mark_as_read(self, notification_id: str, user_id: str) -> None:
        """Mark a notification as read"""
        notification = self.notification_repo.get_by_id(notification_id)
        if notification and notification.user_id == user_id:
            self.notification_repo.mark_as_read(notification_id)
    
    def mark_all_read(self, user_id: str) -> None:
        """Mark all notifications as read for a user"""
        self.notification_repo.mark_all_as_read(user_id)
    
    def notify_plan_update(self, plan, modifier_id: str):
        """Helper to notify relevant parties about plan update"""
        # If modifier is trainer, notify client
        # If modifier is client, notify trainer
        # Logic depends on who 'plan.user_id' is vs 'modifier_id'
        
        if modifier_id == plan.user_id:
            # Client modified (unlikely for approved plans, but possible for drafts)
            # Notify trainer if assigned
            pass # Logic to find trainer needed
        else:
            # Trainer modified, notify client
            self.create_notification(
                user_id=plan.user_id,
                type=NotificationType.PLAN_UPDATED,
                title="Plan Updated",
                message=f"Your {type(plan).__name__} has been updated by your trainer.",
                related_entity_type="workout_plan" if "Workout" in type(plan).__name__ else "nutrition_plan",
                related_entity_id=plan.id
            )
