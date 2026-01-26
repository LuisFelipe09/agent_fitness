from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import WorkoutPlan, WorkoutDay, Exercise, Goal, ActivityLevel
from src.domain.repositories import WorkoutPlanRepository, PlanRepository
from src.infrastructure.orm_models import WorkoutPlanORM
from dataclasses import asdict

class SqlAlchemyWorkoutPlanRepository(WorkoutPlanRepository):
    def __init__(self, db: Session):
        self.db = db

    def _deserialize_workout_days(self, sessions_data: List[dict]) -> List[WorkoutDay]:
        """Deserialize JSON workout days data from the DB to Domain Objects"""
        if not sessions_data:
            return []
        
        workout_days = []
        for s_data in sessions_data:
            exercises = []
            if 'exercises' in s_data:
                for e_data in s_data['exercises']:
                    exercises.append(Exercise(
                        name=e_data.get('name', ''),
                        sets=e_data.get('sets', 0),
                        reps=e_data.get('reps', ''),
                        rest=e_data.get('rest', e_data.get('rest_time', '')),  # Handle both 'rest' and legacy 'rest_time'
                        notes=e_data.get('notes'),
                        description=e_data.get('description'), # Legacy field
                        video_url=e_data.get('video_url')
                    ))
            
            workout_days.append(WorkoutDay(
                day=s_data.get('day', ''),
                focus=s_data.get('focus', ''),
                exercises=exercises
            ))
        return workout_days

    def _extract_plan_metadata(self, sessions_data: dict) -> dict:
        """Extract plan metadata from sessions_data JSON if stored there"""
        if isinstance(sessions_data, dict):
            return {
                'title': sessions_data.get('title', 'Workout Plan'),
                'description': sessions_data.get('description', ''),
                'weeks': sessions_data.get('weeks', 4),
                'days_per_week': sessions_data.get('days_per_week', 3),
                'workout_days': sessions_data.get('workout_days', sessions_data.get('sessions', []))
            }
        # If sessions_data is a list, it's legacy format (just workout days)
        return {
            'title': 'Workout Plan',
            'description': '',
            'weeks': 4,
            'days_per_week': 3,
            'workout_days': sessions_data if isinstance(sessions_data, list) else []
        }

    def _orm_to_domain(self, plan_orm: WorkoutPlanORM) -> WorkoutPlan:
        """Convert ORM model to domain model"""
        metadata = self._extract_plan_metadata(plan_orm.sessions_data)
        workout_days_list = metadata['workout_days']
        
        return WorkoutPlan(
            id=plan_orm.id,
            user_id=plan_orm.user_id,
            title=metadata['title'],
            description=metadata['description'],
            weeks=metadata['weeks'],
            days_per_week=metadata['days_per_week'],
            workout_days=self._deserialize_workout_days(workout_days_list),
            created_at=plan_orm.created_at,
            updated_at=plan_orm.updated_at, # Changed from modified_at
            created_by=plan_orm.created_by,
            approved_by=None,
            approved_at=None,
            state=plan_orm.state if plan_orm.state else "draft",
            goal=Goal(plan_orm.goal) if plan_orm.goal else None,
            target_activity_level=ActivityLevel(plan_orm.target_activity_level) if plan_orm.target_activity_level else None
        )

    def get_current_plan(self, user_id: str) -> Optional[WorkoutPlan]:
        # Get the latest plan
        plan_orm = self.db.query(WorkoutPlanORM).filter(WorkoutPlanORM.user_id == user_id).order_by(WorkoutPlanORM.created_at.desc()).first()
        if not plan_orm:
            return None
        
        return self._orm_to_domain(plan_orm)

    def save(self, plan: WorkoutPlan) -> None:
        # Serialize workout_days to JSON with metadata
        sessions_data = {
            'title': plan.title,
            'description': plan.description,
            'weeks': plan.weeks,
            'days_per_week': plan.days_per_week,
            'workout_days': [asdict(wd) for wd in plan.workout_days]
        }
        
        plan_orm = WorkoutPlanORM(
            id=plan.id,
            user_id=plan.user_id,
            created_at=plan.created_at,
            updated_at=plan.updated_at, # Changed from modified_at
            sessions_data=sessions_data,
            created_by=plan.created_by,
            state=plan.state,
            goal=plan.goal.value if plan.goal else None,
            target_activity_level=plan.target_activity_level.value if plan.target_activity_level else None
        )
        self.db.add(plan_orm)
        self.db.commit()
    
    def get_by_id(self, plan_id: str) -> Optional[WorkoutPlan]:
        """Get a workout plan by its ID"""
        plan_orm = self.db.query(WorkoutPlanORM).filter(WorkoutPlanORM.id == plan_id).first()
        if not plan_orm:
            return None
        
        return self._orm_to_domain(plan_orm)
    
    def update(self, plan: WorkoutPlan) -> None:
        """Update an existing workout plan"""
        plan_orm = self.db.query(WorkoutPlanORM).filter(WorkoutPlanORM.id == plan.id).first()
        if plan_orm:
            # Serialize workout_days to JSON with metadata
            sessions_data = {
                'title': plan.title,
                'description': plan.description,
                'weeks': plan.weeks,
                'days_per_week': plan.days_per_week,
                'workout_days': [asdict(wd) for wd in plan.workout_days]
            }
            
            plan_orm.sessions_data = sessions_data
            plan_orm.updated_at = plan.updated_at # Changed from modified_at
            plan_orm.state = plan.state
            plan_orm.goal = plan.goal.value if plan.goal else None
            plan_orm.target_activity_level = plan.target_activity_level.value if plan.target_activity_level else None
            self.db.commit()
