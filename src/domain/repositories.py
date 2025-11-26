from abc import ABC, abstractmethod
from typing import Optional
from .models import User, WorkoutPlan, NutritionPlan

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
    def get_current_plan(self, user_id: str) -> Optional[NutritionPlan]:
        pass

    @abstractmethod
    def save(self, plan: NutritionPlan) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[NutritionPlan]:
        """Get a nutrition plan by its ID"""
        pass
    
    @abstractmethod
    def update(self, plan: NutritionPlan) -> None:
        """Update an existing nutrition plan"""
        pass
