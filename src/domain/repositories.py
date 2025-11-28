from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic
from .models import User, WorkoutPlan, NutritionPlan, PlanVersion, PlanComment, Notification

# Generic Type for Plans
T = TypeVar('T', bound='WorkoutPlan | NutritionPlan')

class PlanRepository(ABC, Generic[T]):
    """Generic interface for plan repositories"""
    @abstractmethod
    def save(self, plan: T) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    def update(self, plan: T) -> None:
        pass
        
    @abstractmethod
    def get_current_plan(self, user_id: str) -> Optional[T]:
        pass

class UserRepository(ABC):
    """Basic CRUD operations for users"""
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def update(self, user: User) -> None:
        pass

class UserQueryRepository(ABC):
    """Query operations for users"""
    @abstractmethod
    def get_by_role(self, role: str) -> List[User]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[User]:
        pass

class UserRelationshipRepository(ABC):
    """Relationship operations for users (trainer/nutritionist clients)"""
    @abstractmethod
    def get_clients_by_trainer(self, trainer_id: str) -> List[User]:
        pass
    
    @abstractmethod
    def get_clients_by_nutritionist(self, nutritionist_id: str) -> List[User]:
        pass

class CompleteUserRepository(UserRepository, UserQueryRepository, UserRelationshipRepository, ABC):
    """Composite interface for full user repository functionality"""
    pass

class WorkoutPlanRepository(PlanRepository[WorkoutPlan]):
    """Workout specific operations"""
    pass

class NutritionPlanRepository(PlanRepository[NutritionPlan]):
    """Nutrition specific operations"""
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
