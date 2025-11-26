from abc import ABC, abstractmethod
from src.domain.models import UserProfile, WorkoutPlan, NutritionPlan

class AIService(ABC):
    @abstractmethod
    def generate_workout_plan(self, profile: UserProfile) -> WorkoutPlan:
        pass

    @abstractmethod
    def generate_nutrition_plan(self, profile: UserProfile) -> NutritionPlan:
        pass
