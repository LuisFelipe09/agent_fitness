from datetime import datetime
from typing import List, Optional
import uuid
from src.domain.models import PlanComment
from src.domain.repositories import PlanCommentRepository

class CommentService:
    def __init__(self, comment_repo: PlanCommentRepository):
        self.comment_repo = comment_repo
    
    def add_comment(self, plan_id: str, plan_type: str, author_id: str, author_role: str, content: str, is_internal: bool = False) -> PlanComment:
        """Add a comment to a plan"""
        comment = PlanComment(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            plan_type=plan_type,
            author_id=author_id,
            author_role=author_role,
            content=content,
            created_at=datetime.now(),
            is_internal=is_internal
        )
        self.comment_repo.save(comment)
        return comment
    
    def get_plan_comments(self, plan_id: str, user_role: str = "client") -> List[PlanComment]:
        """Get comments for a plan, filtering internal ones if user is client"""
        comments = self.comment_repo.get_by_plan_id(plan_id)
        
        if user_role == "client":
            # Clients don't see internal comments
            return [c for c in comments if not c.is_internal]
        
        return comments
    
    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete a comment (only author can delete)"""
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            return False
        
        if comment.author_id != user_id:
            raise PermissionError("You can only delete your own comments")
            
        self.comment_repo.delete(comment_id)
        return True
