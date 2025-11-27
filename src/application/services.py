from typing import Optional, TypeVar, Generic
from datetime import datetime
from src.domain.models import (
    User, UserProfile, WorkoutPlan, NutritionPlan,
    WorkoutSession, Exercise, DailyMealPlan, Meal
)
from src.domain.repositories import UserRepository, WorkoutPlanRepository, NutritionPlanRepository
from src.application.interfaces import AIService

# Type variable for generic plan repository
PlanType = TypeVar('PlanType', WorkoutPlan, NutritionPlan)

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

    def _activate_plan(self, plan_id: str, user_id: str, repo):
        """
        Generic method to activate any type of plan.
        - Verifies plan belongs to user and is APPROVED.
        - Archives any currently ACTIVE plan.
        - Sets new plan to ACTIVE.
        
        Args:
            plan_id: ID of the plan to activate
            user_id: ID of the user activating the plan
            repo: Repository instance (WorkoutPlanRepository or NutritionPlanRepository)
        
        Returns:
            The activated plan
        """
        plan = repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        
        if plan.user_id != user_id:
            raise ValueError("Plan does not belong to this user")
            
        if plan.state != "approved":
            raise ValueError(f"Cannot activate plan in '{plan.state}' state. Only 'approved' plans can be activated.")
            
        # Archive current active plan
        current_active = repo.get_current_plan(user_id)
        if current_active and current_active.id != plan_id:
            if current_active.state == "active":
                current_active.state = "archived"
                repo.update(current_active)
        
        plan.state = "active"
        repo.update(plan)
        return plan

    def activate_workout_plan(self, plan_id: str, user_id: str) -> WorkoutPlan:
        """Activates a workout plan (delegates to generic method)"""
        return self._activate_plan(plan_id, user_id, self.workout_repo)

    def activate_nutrition_plan(self, plan_id: str, user_id: str) -> NutritionPlan:
        """Activates a nutrition plan (delegates to generic method)"""
        return self._activate_plan(plan_id, user_id, self.nutrition_repo)

    def update_workout_plan(
        self,
        plan_id: str,
        start_date: datetime,
        end_date: datetime,
        sessions: list[WorkoutSession],
        modified_by: str
    ) -> WorkoutPlan:
        """
        Updates a workout plan with new data.
        
        Args:
            plan_id: ID of the plan to update
            start_date: New start date
            end_date: New end date
            sessions: List of workout sessions
            modified_by: ID of user making the modification
            
        Returns:
            Updated workout plan
        """
        existing_plan = self.workout_repo.get_by_id(plan_id)
        if not existing_plan:
            raise ValueError("Workout plan not found")
        
        updated_plan = WorkoutPlan(
            id=existing_plan.id,
            user_id=existing_plan.user_id,
            start_date=start_date,
            end_date=end_date,
            sessions=sessions,
            created_at=existing_plan.created_at,
            created_by=existing_plan.created_by,
            modified_at=datetime.now(),
            modified_by=modified_by,
            state="approved"  # Trainer/nutritionist approved
        )
        
        self.workout_repo.update(updated_plan)
        return updated_plan

    def update_nutrition_plan(
        self,
        plan_id: str,
        start_date: datetime,
        end_date: datetime,
        daily_plans: list[DailyMealPlan],
        modified_by: str
    ) -> NutritionPlan:
        """
        Updates a nutrition plan with new data.
        
        Args:
            plan_id: ID of the plan to update
            start_date: New start date
            end_date: New end date
            daily_plans: List of daily meal plans
            modified_by: ID of user making the modification
            
        Returns:
            Updated nutrition plan
        """
        existing_plan = self.nutrition_repo.get_by_id(plan_id)
        if not existing_plan:
            raise ValueError("Nutrition plan not found")
        
        updated_plan = NutritionPlan(
            id=existing_plan.id,
            user_id=existing_plan.user_id,
            start_date=start_date,
            end_date=end_date,
            daily_plans=daily_plans,
            created_at=existing_plan.created_at,
            created_by=existing_plan.created_by,
            modified_at=datetime.now(),
            modified_by=modified_by,
            state="approved"  # Trainer/nutritionist approved
        )
        
        self.nutrition_repo.update(updated_plan)
        return updated_plan
