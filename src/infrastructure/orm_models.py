from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class UserORM(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Roles stored as JSON array for flexibility
    roles = Column(JSON, default=["client"])
    
    # Profile data stored as JSON for simplicity in this MVP, 
    # but could be normalized in a real app
    profile_data = Column(JSON, nullable=True)
    
    # Authentication fields
    password_hash = Column(String, nullable=True)  # For web login
    email = Column(String, unique=True, nullable=True, index=True)
    
    # Relationships with trainer and nutritionist
    trainer_id = Column(String, ForeignKey("users.id"), nullable=True)
    nutritionist_id = Column(String, ForeignKey("users.id"), nullable=True)

    workout_plans = relationship("WorkoutPlanORM", back_populates="user", foreign_keys="WorkoutPlanORM.user_id")
    nutrition_plans = relationship("NutritionPlanORM", back_populates="user", foreign_keys="NutritionPlanORM.user_id")
    notifications = relationship("NotificationORM", back_populates="user")

class WorkoutPlanORM(Base):
    __tablename__ = "workout_plans"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # Storing complex nested structures as JSON for flexibility with AI outputs
    sessions_data = Column(JSON)
    
    # Traceability fields
    created_by = Column(String, nullable=True)  # User ID who created
    modified_at = Column(DateTime, nullable=True)
    modified_by = Column(String, nullable=True)  # User ID who modified
    
    # State management
    state = Column(String, default="draft")  # draft, under_review, approved, active, completed

    user = relationship("UserORM", back_populates="workout_plans", foreign_keys=[user_id])

class NutritionPlanORM(Base):
    __tablename__ = "nutrition_plans"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # Storing complex nested structures as JSON
    daily_plans_data = Column(JSON)
    
    # Traceability fields
    created_by = Column(String, nullable=True)  # User ID who created
    modified_at = Column(DateTime, nullable=True)
    modified_by = Column(String, nullable=True)  # User ID who modified
    
    # State management
    state = Column(String, default="draft")  # draft, under_review, approved, active, completed

    user = relationship("UserORM", back_populates="nutrition_plans", foreign_keys=[user_id])

class PlanVersionORM(Base):
    """Version history for workout and nutrition plans"""
    __tablename__ = "plan_versions"
    
    id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, index=True, nullable=False)  # ID of the plan
    plan_type = Column(String, nullable=False)  # "workout" or "nutrition"
    version_number = Column(Integer, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    changes_summary = Column(Text)
    data_snapshot = Column(JSON, nullable=False)  # Complete snapshot
    state_at_version = Column(String, nullable=False)

class PlanCommentORM(Base):
    """Comments on workout and nutrition plans"""
    __tablename__ = "plan_comments"
    
    id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, index=True, nullable=False)
    plan_type = Column(String, nullable=False)  # "workout" or "nutrition"
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    author_role = Column(String, nullable=False)  # client, trainer, nutritionist
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    edited_at = Column(DateTime, nullable=True)
    is_internal = Column(Boolean, default=False)  # Only for professionals

class NotificationORM(Base):
    """Notifications for users"""
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    type = Column(String, nullable=False)  # From NotificationType enum
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    related_entity_type = Column(String, nullable=True)  # "workout_plan", etc
    related_entity_id = Column(String, nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    user = relationship("UserORM", back_populates="notifications")
