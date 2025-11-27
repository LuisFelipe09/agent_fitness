from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import Notification
from src.domain.repositories import NotificationRepository
from src.infrastructure.orm_models import NotificationORM

class SqlAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, notification: Notification) -> None:
        notification_orm = NotificationORM(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            related_entity_type=notification.related_entity_type,
            related_entity_id=notification.related_entity_id,
            is_read=notification.is_read,
            created_at=notification.created_at,
            read_at=notification.read_at
        )
        self.db.merge(notification_orm)
        self.db.commit()
    
    def get_by_user_id(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        query = self.db.query(NotificationORM).filter(NotificationORM.user_id == user_id)
        if unread_only:
            query = query.filter(NotificationORM.is_read == False)
        
        notifications_orm = query.order_by(NotificationORM.created_at.desc()).all()
        return [
            Notification(
                id=n.id,
                user_id=n.user_id,
                type=n.type,
                title=n.title,
                message=n.message,
                related_entity_type=n.related_entity_type,
                related_entity_id=n.related_entity_id,
                is_read=n.is_read,
                created_at=n.created_at,
                read_at=n.read_at
            )
            for n in notifications_orm
        ]
    
    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        n = self.db.query(NotificationORM).filter(NotificationORM.id == notification_id).first()
        if not n:
            return None
        return Notification(
            id=n.id,
            user_id=n.user_id,
            type=n.type,
            title=n.title,
            message=n.message,
            related_entity_type=n.related_entity_type,
            related_entity_id=n.related_entity_id,
            is_read=n.is_read,
            created_at=n.created_at,
            read_at=n.read_at
        )
    
    def mark_as_read(self, notification_id: str) -> None:
        from datetime import datetime
        self.db.query(NotificationORM).filter(NotificationORM.id == notification_id).update(
            {"is_read": True, "read_at": datetime.now()}
        )
        self.db.commit()
    
    def mark_all_as_read(self, user_id: str) -> None:
        from datetime import datetime
        self.db.query(NotificationORM).filter(NotificationORM.user_id == user_id, NotificationORM.is_read == False).update(
            {"is_read": True, "read_at": datetime.now()}
        )
        self.db.commit()
