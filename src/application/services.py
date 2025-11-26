from typing import Optional
from src.domain.models import User, UserProfile, WorkoutPlan, NutritionPlan
from src.domain.repositories import UserRepository, WorkoutPlanRepository, NutritionPlanRepository
from src.application.interfaces import AIService

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_user(self, user_id: str, username: str) -> User:
        existing_user = self.user_repo.get_by_id(user_id)
        if existing_user:
            return existing_user
        
        new_user = User(id=user_id, username=username)
        self.user_repo.save(new_user)
        return new_user

    def update_profile(self, user_id: str, profile: UserProfile) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.profile = profile
        self.user_repo.update(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

class PlanningService:
    def __init__(
        self,
        ai_service: AIService,
        workout_repo: WorkoutPlanRepository,
        nutrition_repo: NutritionPlanRepository,
        user_repo: UserRepository
    ):
        self.ai_service = ai_service
        self.workout_repo = workout_repo
        self.nutrition_repo = nutrition_repo
        self.user_repo = user_repo

    def generate_workout_plan(self, user_id: str) -> WorkoutPlan:
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.profile:
            raise ValueError("User profile incomplete or not found")

        plan = self.ai_service.generate_workout_plan(user.profile)
        plan.user_id = user_id # Ensure the plan is linked to the user
        plan.created_by = user_id  # Track who created the plan
        plan.state = "draft"  # Initial state
        self.workout_repo.save(plan)
        return plan

    def generate_nutrition_plan(self, user_id: str) -> NutritionPlan:
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.profile:
            raise ValueError("User profile incomplete or not found")

        plan = self.ai_service.generate_nutrition_plan(user.profile)
        plan.user_id = user_id
        plan.created_by = user_id  # Track who created the plan
        plan.state = "draft"  # Initial state
        self.nutrition_repo.save(plan)
        return plan
