from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON, DateTime
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
    
    # Relationships with trainer and nutritionist
    trainer_id = Column(String, ForeignKey("users.id"), nullable=True)
    nutritionist_id = Column(String, ForeignKey("users.id"), nullable=True)

    workout_plans = relationship("WorkoutPlanORM", back_populates="user")
    nutrition_plans = relationship("NutritionPlanORM", back_populates="user")

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

    user = relationship("UserORM", back_populates="workout_plans")

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

    user = relationship("UserORM", back_populates="nutrition_plans")
