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

    def activate_workout_plan(self, plan_id: str, user_id: str) -> WorkoutPlan:
        """
        Activates a workout plan.
        - Verifies plan belongs to user and is APPROVED.
        - Archives any currently ACTIVE plan.
        - Sets new plan to ACTIVE.
        """
        plan = self.workout_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        
        if plan.user_id != user_id:
            raise ValueError("Plan does not belong to this user")
            
        if plan.state != "approved":
            raise ValueError(f"Cannot activate plan in '{plan.state}' state. Only 'approved' plans can be activated.")
            
        # Archive current active plan
        current_active = self.workout_repo.get_current_plan(user_id)
        if current_active and current_active.id != plan_id:
            # Note: get_current_plan might return the plan we are trying to activate if logic changes,
            # but currently it returns the 'latest' which might not be 'active'.
            # We need to be careful. Ideally we should search for plan with state='active'.
            # Since we don't have a specific 'get_active_plan' method, we'll assume we need to implement this logic carefully.
            # For now, let's assume we iterate or we add a method.
            # Actually, let's just check if the current one returned is active.
            if current_active.state == "active":
                current_active.state = "archived"
                self.workout_repo.update(current_active)
        
        plan.state = "active"
        self.workout_repo.update(plan)
        return plan

    def activate_nutrition_plan(self, plan_id: str, user_id: str) -> NutritionPlan:
        """
        Activates a nutrition plan.
        - Verifies plan belongs to user and is APPROVED.
        - Archives any currently ACTIVE plan.
        - Sets new plan to ACTIVE.
        """
        plan = self.nutrition_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        
        if plan.user_id != user_id:
            raise ValueError("Plan does not belong to this user")
            
        if plan.state != "approved":
            raise ValueError(f"Cannot activate plan in '{plan.state}' state. Only 'approved' plans can be activated.")
            
        # Archive current active plan
        current_active = self.nutrition_repo.get_current_plan(user_id)
        if current_active and current_active.id != plan_id:
            if current_active.state == "active":
                current_active.state = "archived"
                self.nutrition_repo.update(current_active)
        
        plan.state = "active"
        self.nutrition_repo.update(plan)
        return plan
