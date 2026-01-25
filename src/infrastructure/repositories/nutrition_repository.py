from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import NutritionPlan, DailyMealPlan, Meal, Goal, ActivityLevel
from src.domain.repositories import NutritionPlanRepository, PlanRepository
from src.infrastructure.orm_models import NutritionPlanORM
from dataclasses import asdict

class SqlAlchemyNutritionPlanRepository(NutritionPlanRepository):
    def __init__(self, db: Session):
        self.db = db

    def _deserialize_daily_plans(self, daily_plans_data: List[dict]) -> List[DailyMealPlan]:
        if not daily_plans_data:
            return []
        
        daily_plans = []
        for d_data in daily_plans_data:
            meals = []
            if 'meals' in d_data:
                for m_data in d_data['meals']:
                    meals.append(Meal(
                        name=m_data.get('name', ''),
                        description=m_data.get('description', ''),
                        calories=m_data.get('calories', 0),
                        protein=m_data.get('protein', 0),
                        carbs=m_data.get('carbs', 0),
                        fats=m_data.get('fats', 0),
                        ingredients=m_data.get('ingredients', [])
                    ))
            
            daily_plans.append(DailyMealPlan(
                day=d_data.get('day', ''),
                meals=meals
            ))
        return daily_plans

    def get_current_plan(self, user_id: str) -> Optional[NutritionPlan]:
        plan_orm = self.db.query(NutritionPlanORM).filter(NutritionPlanORM.user_id == user_id).order_by(NutritionPlanORM.created_at.desc()).first()
        if not plan_orm:
            return None
            
        return NutritionPlan(
            id=plan_orm.id,
            user_id=plan_orm.user_id,
            start_date=plan_orm.start_date,
            end_date=plan_orm.end_date,
            daily_plans=self._deserialize_daily_plans(plan_orm.daily_plans_data),
            created_at=plan_orm.created_at,
            created_by=plan_orm.created_by,
            modified_at=plan_orm.modified_at,
            modified_by=plan_orm.modified_by,
            state=plan_orm.state if plan_orm.state else "draft",
            goal=Goal(plan_orm.goal) if plan_orm.goal else None,  # Deserialize string to enum
            target_activity_level=ActivityLevel(plan_orm.target_activity_level) if plan_orm.target_activity_level else None
        )

    def save(self, plan: NutritionPlan) -> None:
        # Serialize meal data - use meals array (new format) or daily_plans (legacy)
        if plan.meals:
            # New format: single day template with meals array
            daily_plans_data = [{"day": "Template", "meals": [asdict(m) for m in plan.meals]}]
        else:
            # Legacy format: multiple daily plans
            daily_plans_data = [asdict(d) for d in plan.daily_plans]
        
        plan_orm = NutritionPlanORM(
            id=plan.id,
            user_id=plan.user_id,
            start_date=plan.created_at,  # NutritionPlan doesn't have start_date, use created_at
            end_date=plan.created_at,    # Same for end_date
            created_at=plan.created_at,
            daily_plans_data=daily_plans_data,
            created_by=plan.created_by,
            modified_at=plan.updated_at,  # Model uses updated_at, ORM uses modified_at
            modified_by=None,  # Not used in new model
            state=plan.state,
            goal=plan.goal.value if plan.goal else None,  # Serialize enum to string
            target_activity_level=plan.target_activity_level.value if plan.target_activity_level else None
        )
        self.db.add(plan_orm)
        self.db.commit()
    
    def get_by_id(self, plan_id: str) -> Optional[NutritionPlan]:
        """Get a nutrition plan by its ID"""
        plan_orm = self.db.query(NutritionPlanORM).filter(NutritionPlanORM.id == plan_id).first()
        if not plan_orm:
            return None
            
        return NutritionPlan(
            id=plan_orm.id,
            user_id=plan_orm.user_id,
            start_date=plan_orm.start_date,
            end_date=plan_orm.end_date,
            daily_plans=self._deserialize_daily_plans(plan_orm.daily_plans_data),
            created_at=plan_orm.created_at,
            created_by=plan_orm.created_by,
            modified_at=plan_orm.modified_at,
            modified_by=plan_orm.modified_by,
            state=plan_orm.state if plan_orm.state else "draft",
            goal=Goal(plan_orm.goal) if plan_orm.goal else None,  # Deserialize string to enum
            target_activity_level=ActivityLevel(plan_orm.target_activity_level) if plan_orm.target_activity_level else None
        )
    
    def update(self, plan: NutritionPlan) -> None:
        """Update an existing nutrition plan"""
        plan_orm = self.db.query(NutritionPlanORM).filter(NutritionPlanORM.id == plan.id).first()
        if plan_orm:
            daily_plans_data = [asdict(d) for d in plan.daily_plans]
            
            plan_orm.start_date = plan.start_date
            plan_orm.end_date = plan.end_date
            plan_orm.daily_plans_data = daily_plans_data
            plan_orm.modified_at = plan.modified_at
            plan_orm.modified_by = plan.modified_by
            plan_orm.state = plan.state
            plan_orm.goal = plan.goal.value if plan.goal else None
            plan_orm.target_activity_level = plan.target_activity_level.value if plan.target_activity_level else None
            self.db.commit()
