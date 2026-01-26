from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import NutritionPlan, DailyMealPlan, Meal, Goal, ActivityLevel
from src.domain.repositories import NutritionPlanRepository, PlanRepository
from src.infrastructure.orm_models import NutritionPlanORM
from dataclasses import asdict

class SqlAlchemyNutritionPlanRepository(NutritionPlanRepository):
    def __init__(self, db: Session):
        self.db = db

    def _deserialize_meal_data(self, data: dict) -> Meal:
        """Deserialize a single meal dictionary to Meal object"""
        return Meal(
            name=data.get('name', 'Unknown Meal'),
            time=data.get('time', '12:00 PM'), # Default if missing
            foods=data.get('foods', data.get('ingredients', [])), # Handle both foods and legacy ingredients
            calories=data.get('calories', 0),
            protein=data.get('protein', 0),
            carbs=data.get('carbs', 0),
            fats=data.get('fats', 0),
            description=data.get('description')
        )

    def _deserialize_daily_plans(self, daily_plans_data: List[dict]) -> List[DailyMealPlan]:
        """Deserialize legacy daily plans list"""
        if not daily_plans_data:
            return []
        
        daily_plans = []
        for d_data in daily_plans_data:
            meals = []
            if 'meals' in d_data:
                for m_data in d_data['meals']:
                    meals.append(self._deserialize_meal_data(m_data))
            
            daily_plans.append(DailyMealPlan(
                day=d_data.get('day', ''),
                meals=meals
            ))
        return daily_plans

    def _extract_plan_data(self, json_data: dict) -> dict:
        """Extract plan data from JSON blob"""
        data = {
            'title': 'Nutrition Plan',
            'description': '',
            'daily_calories': 2000,
            'protein_grams': 150,
            'carbs_grams': 200,
            'fats_grams': 65,
            'meals': [],
            'daily_plans': []
        }
        
        if not json_data:
            return data

        # If it's a list, it's the legacy daily_plans format
        if isinstance(json_data, list):
             data['daily_plans'] = self._deserialize_daily_plans(json_data)
             return data
             
        # Otherwise it's the new dict format
        data['title'] = json_data.get('title', data['title'])
        data['description'] = json_data.get('description', data['description'])
        data['daily_calories'] = json_data.get('daily_calories', data['daily_calories'])
        data['protein_grams'] = json_data.get('protein_grams', data['protein_grams'])
        data['carbs_grams'] = json_data.get('carbs_grams', data['carbs_grams'])
        data['fats_grams'] = json_data.get('fats_grams', data['fats_grams'])
        
        # Parse meals (template)
        if 'meals' in json_data:
            data['meals'] = [self._deserialize_meal_data(m) for m in json_data['meals']]
            
        # Parse daily_plans (if any)
        if 'daily_plans' in json_data:
            data['daily_plans'] = self._deserialize_daily_plans(json_data['daily_plans'])
            
        return data

    def _orm_to_domain(self, plan_orm: NutritionPlanORM) -> NutritionPlan:
        """Convert ORM model to domain model"""
        plan_data = self._extract_plan_data(plan_orm.daily_plans_data)
        
        return NutritionPlan(
            id=plan_orm.id,
            user_id=plan_orm.user_id,
            title=plan_data['title'],
            description=plan_data['description'],
            daily_calories=plan_data['daily_calories'],
            protein_grams=plan_data['protein_grams'],
            carbs_grams=plan_data['carbs_grams'],
            fats_grams=plan_data['fats_grams'],
            meals=plan_data['meals'],
            daily_plans=plan_data['daily_plans'],
            created_at=plan_orm.created_at,
            updated_at=plan_orm.updated_at, # Changed from modified_at
            created_by=plan_orm.created_by,
            approved_by=None,
            approved_at=None,
            state=plan_orm.state if plan_orm.state else "draft",
            goal=Goal(plan_orm.goal) if plan_orm.goal else None,
            target_activity_level=ActivityLevel(plan_orm.target_activity_level) if plan_orm.target_activity_level else None
        )

    def get_current_plan(self, user_id: str) -> Optional[NutritionPlan]:
        plan_orm = self.db.query(NutritionPlanORM).filter(NutritionPlanORM.user_id == user_id).order_by(NutritionPlanORM.created_at.desc()).first()
        if not plan_orm:
            return None
            
        return self._orm_to_domain(plan_orm)

    def save(self, plan: NutritionPlan) -> None:
        # Serialize all plan data to JSON
        plan_data = {
            'title': plan.title,
            'description': plan.description,
            'daily_calories': plan.daily_calories,
            'protein_grams': plan.protein_grams,
            'carbs_grams': plan.carbs_grams,
            'fats_grams': plan.fats_grams,
            'meals': [asdict(m) for m in plan.meals],
            'daily_plans': [asdict(d) for d in plan.daily_plans]
        }
        
        plan_orm = NutritionPlanORM(
            id=plan.id,
            user_id=plan.user_id,
            created_at=plan.created_at,
            daily_plans_data=plan_data, # Store full blob here
            created_by=plan.created_by,
            updated_at=plan.updated_at, # Changed from modified_at
            state=plan.state,
            goal=plan.goal.value if plan.goal else None,
            target_activity_level=plan.target_activity_level.value if plan.target_activity_level else None
        )
        self.db.add(plan_orm)
        self.db.commit()
    
    def get_by_id(self, plan_id: str) -> Optional[NutritionPlan]:
        """Get a nutrition plan by its ID"""
        plan_orm = self.db.query(NutritionPlanORM).filter(NutritionPlanORM.id == plan_id).first()
        if not plan_orm:
            return None
            
        return self._orm_to_domain(plan_orm)
    
    def update(self, plan: NutritionPlan) -> None:
        """Update an existing nutrition plan"""
        plan_orm = self.db.query(NutritionPlanORM).filter(NutritionPlanORM.id == plan.id).first()
        if plan_orm:
            plan_data = {
                'title': plan.title,
                'description': plan.description,
                'daily_calories': plan.daily_calories,
                'protein_grams': plan.protein_grams,
                'carbs_grams': plan.carbs_grams,
                'fats_grams': plan.fats_grams,
                'meals': [asdict(m) for m in plan.meals],
                'daily_plans': [asdict(d) for d in plan.daily_plans]
            }
            
            plan_orm.daily_plans_data = plan_data
            plan_orm.updated_at = plan.updated_at # Changed from modified_at
            plan_orm.state = plan.state
            plan_orm.goal = plan.goal.value if plan.goal else None
            plan_orm.target_activity_level = plan.target_activity_level.value if plan.target_activity_level else None
            self.db.commit()
