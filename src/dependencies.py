from fastapi import Depends
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db
from src.domain.repositories import (
    UserRepository, 
    CompleteUserRepository,
    WorkoutPlanRepository, 
    NutritionPlanRepository,
    PlanVersionRepository,
    PlanCommentRepository,
    NotificationRepository
)
from src.infrastructure.repositories import (
    SqlAlchemyUserRepository, 
    SqlAlchemyWorkoutPlanRepository, 
    SqlAlchemyNutritionPlanRepository,
    SqlAlchemyPlanVersionRepository,
    SqlAlchemyPlanCommentRepository,
    SqlAlchemyNotificationRepository
)
from src.application.user_service import UserService
from src.application.planning_service import PlanningService
from src.application.role_service import RoleService
from src.application.version_service import VersionService
from src.application.comment_service import CommentService
from src.application.notification_service import NotificationService
from src.application.interfaces import AIService
from src.infrastructure.ai_service import GeminiAIService

import os

# Repository Providers
def get_user_repository(db: Session = Depends(get_db)) -> CompleteUserRepository:
    return SqlAlchemyUserRepository(db)

def get_workout_repository(db: Session = Depends(get_db)) -> WorkoutPlanRepository:
    return SqlAlchemyWorkoutPlanRepository(db)

def get_nutrition_repository(db: Session = Depends(get_db)) -> NutritionPlanRepository:
    return SqlAlchemyNutritionPlanRepository(db)

def get_version_repository(db: Session = Depends(get_db)) -> PlanVersionRepository:
    return SqlAlchemyPlanVersionRepository(db)

def get_comment_repository(db: Session = Depends(get_db)) -> PlanCommentRepository:
    return SqlAlchemyPlanCommentRepository(db)

def get_notification_repository(db: Session = Depends(get_db)) -> NotificationRepository:
    return SqlAlchemyNotificationRepository(db)

import os

# Service Providers
def get_ai_service() -> AIService:
    api_key = os.getenv("GEMINI_API_KEY", "dummy_key")
    return GeminiAIService(api_key)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)

def get_planning_service(
    ai_service: AIService = Depends(get_ai_service),
    workout_repo: WorkoutPlanRepository = Depends(get_workout_repository),
    nutrition_repo: NutritionPlanRepository = Depends(get_nutrition_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> PlanningService:
    return PlanningService(ai_service, workout_repo, nutrition_repo, user_repo)

def get_role_service(user_repo: UserRepository = Depends(get_user_repository)) -> RoleService:
    return RoleService(user_repo)

def get_version_service(version_repo: PlanVersionRepository = Depends(get_version_repository)) -> VersionService:
    return VersionService(version_repo)

def get_comment_service(comment_repo: PlanCommentRepository = Depends(get_comment_repository)) -> CommentService:
    return CommentService(comment_repo)

def get_notification_service(notification_repo: NotificationRepository = Depends(get_notification_repository)) -> NotificationService:
    return NotificationService(notification_repo)
