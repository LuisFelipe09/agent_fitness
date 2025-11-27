from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import PlanComment
from src.domain.repositories import PlanCommentRepository
from src.infrastructure.orm_models import PlanCommentORM

class SqlAlchemyPlanCommentRepository(PlanCommentRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, comment: PlanComment) -> None:
        comment_orm = PlanCommentORM(
            id=comment.id,
            plan_id=comment.plan_id,
            plan_type=comment.plan_type,
            author_id=comment.author_id,
            author_role=comment.author_role,
            content=comment.content,
            created_at=comment.created_at,
            edited_at=comment.edited_at,
            is_internal=comment.is_internal
        )
        self.db.merge(comment_orm)  # Use merge to handle both insert and update
        self.db.commit()
    
    def get_by_plan_id(self, plan_id: str) -> List[PlanComment]:
        comments_orm = self.db.query(PlanCommentORM).filter(PlanCommentORM.plan_id == plan_id).order_by(PlanCommentORM.created_at.asc()).all()
        return [
            PlanComment(
                id=c.id,
                plan_id=c.plan_id,
                plan_type=c.plan_type,
                author_id=c.author_id,
                author_role=c.author_role,
                content=c.content,
                created_at=c.created_at,
                edited_at=c.edited_at,
                is_internal=c.is_internal
            )
            for c in comments_orm
        ]
    
    def get_by_id(self, comment_id: str) -> Optional[PlanComment]:
        c = self.db.query(PlanCommentORM).filter(PlanCommentORM.id == comment_id).first()
        if not c:
            return None
        return PlanComment(
            id=c.id,
            plan_id=c.plan_id,
            plan_type=c.plan_type,
            author_id=c.author_id,
            author_role=c.author_role,
            content=c.content,
            created_at=c.created_at,
            edited_at=c.edited_at,
            is_internal=c.is_internal
        )
    
    def delete(self, comment_id: str) -> None:
        self.db.query(PlanCommentORM).filter(PlanCommentORM.id == comment_id).delete()
        self.db.commit()
