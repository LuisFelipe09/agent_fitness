from abc import ABC, abstractmethod
from typing import Dict, Any
from src.domain.models import UserProfile

class AIService(ABC):
    @abstractmethod
    def generate_workout_plan(self, profile: UserProfile) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_nutrition_plan(self, profile: UserProfile) -> Dict[str, Any]:
        pass
