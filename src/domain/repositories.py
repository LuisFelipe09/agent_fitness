from abc import ABC, abstractmethod
from typing import Optional, List
from .models import User, WorkoutPlan, NutritionPlan, PlanVersion, PlanComment, Notification

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def update(self, user: User) -> None:
        pass

class WorkoutPlanRepository(ABC):
    @abstractmethod
    def get_current_plan(self, user_id: str) -> Optional[WorkoutPlan]:
        pass

    @abstractmethod
    def save(self, plan: WorkoutPlan) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[WorkoutPlan]:
        """Get a workout plan by its ID"""
        pass
    
    @abstractmethod
    def update(self, plan: WorkoutPlan) -> None:
        """Update an existing workout plan"""
        pass

class NutritionPlanRepository(ABC):
    @abstractmethod
    def save(self, plan: NutritionPlan) -> None:
        pass
    
    @abstractmethod
    def get_current_plan(self, user_id: str) -> Optional[NutritionPlan]:
        pass

    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[NutritionPlan]:
        pass

    @abstractmethod
    def update(self, plan: NutritionPlan) -> None:
        pass

class PlanVersionRepository(ABC):
    @abstractmethod
    def save(self, version: PlanVersion) -> None:
        pass
    
    @abstractmethod
    def get_by_plan_id(self, plan_id: str) -> List[PlanVersion]:
        pass
    
    @abstractmethod
    def get_by_id(self, version_id: str) -> Optional[PlanVersion]:
        pass

class PlanCommentRepository(ABC):
    @abstractmethod
    def save(self, comment: PlanComment) -> None:
        pass
    
    @abstractmethod
    def get_by_plan_id(self, plan_id: str) -> List[PlanComment]:
        pass
    
    @abstractmethod
    def get_by_id(self, comment_id: str) -> Optional[PlanComment]:
        pass
    
    @abstractmethod
    def delete(self, comment_id: str) -> None:
        pass

class NotificationRepository(ABC):
    @abstractmethod
    def save(self, notification: Notification) -> None:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        pass
    
    @abstractmethod
    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        pass
    
    @abstractmethod
    def mark_as_read(self, notification_id: str) -> None:
        pass
    
    @abstractmethod
    def mark_all_as_read(self, user_id: str) -> None:
        pass
