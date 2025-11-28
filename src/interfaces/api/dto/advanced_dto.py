from pydantic import BaseModel
from typing import Optional

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
