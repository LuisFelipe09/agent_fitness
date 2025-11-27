from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import WorkoutPlan, WorkoutSession, Exercise
from src.domain.repositories import WorkoutPlanRepository
from src.infrastructure.orm_models import WorkoutPlanORM
from dataclasses import asdict

class SqlAlchemyWorkoutPlanRepository(WorkoutPlanRepository):
    def __init__(self, db: Session):
        self.db = db

    def _deserialize_sessions(self, sessions_data: List[dict]) -> List[WorkoutSession]:
        if not sessions_data:
            return []
        
        sessions = []
        for s_data in sessions_data:
            exercises = []
            if 'exercises' in s_data:
                for e_data in s_data['exercises']:
                    exercises.append(Exercise(
                        name=e_data.get('name', ''),
                        description=e_data.get('description', ''),
                        sets=e_data.get('sets', 0),
                        reps=e_data.get('reps', ''),
                        rest_time=e_data.get('rest_time', ''),
                        video_url=e_data.get('video_url')
                    ))
            
            sessions.append(WorkoutSession(
                day=s_data.get('day', ''),
                focus=s_data.get('focus', ''),
                exercises=exercises
            ))
        return sessions

    def get_current_plan(self, user_id: str) -> Optional[WorkoutPlan]:
        # Get the latest plan
        plan_orm = self.db.query(WorkoutPlanORM).filter(WorkoutPlanORM.user_id == user_id).order_by(WorkoutPlanORM.created_at.desc()).first()
        if not plan_orm:
            return None
        
        return WorkoutPlan(
            id=plan_orm.id,
            user_id=plan_orm.user_id,
            start_date=plan_orm.start_date,
            end_date=plan_orm.end_date,
            sessions=self._deserialize_sessions(plan_orm.sessions_data),
            created_at=plan_orm.created_at,
            created_by=plan_orm.created_by,
            modified_at=plan_orm.modified_at,
            modified_by=plan_orm.modified_by,
            state=plan_orm.state if plan_orm.state else "draft"
        )

    def save(self, plan: WorkoutPlan) -> None:
        # Serialize sessions to JSON
        sessions_data = [asdict(s) for s in plan.sessions]
        
        plan_orm = WorkoutPlanORM(
            id=plan.id,
            user_id=plan.user_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            created_at=plan.created_at,
            sessions_data=sessions_data,
            created_by=plan.created_by,
            modified_at=plan.modified_at,
            modified_by=plan.modified_by,
            state=plan.state
        )
        self.db.add(plan_orm)
        self.db.commit()
    
    def get_by_id(self, plan_id: str) -> Optional[WorkoutPlan]:
        """Get a workout plan by its ID"""
        plan_orm = self.db.query(WorkoutPlanORM).filter(WorkoutPlanORM.id == plan_id).first()
        if not plan_orm:
            return None
        
        return WorkoutPlan(
            id=plan_orm.id,
            user_id=plan_orm.user_id,
            start_date=plan_orm.start_date,
            end_date=plan_orm.end_date,
            sessions=self._deserialize_sessions(plan_orm.sessions_data),
            created_at=plan_orm.created_at,
            created_by=plan_orm.created_by,
            modified_at=plan_orm.modified_at,
            modified_by=plan_orm.modified_by,
            state=plan_orm.state if plan_orm.state else "draft"
        )
    
    def update(self, plan: WorkoutPlan) -> None:
        """Update an existing workout plan"""
        plan_orm = self.db.query(WorkoutPlanORM).filter(WorkoutPlanORM.id == plan.id).first()
        if plan_orm:
            # Serialize sessions to JSON
            sessions_data = [asdict(s) for s in plan.sessions]
            
            plan_orm.start_date = plan.start_date
            plan_orm.end_date = plan.end_date
            plan_orm.sessions_data = sessions_data
            plan_orm.modified_at = plan.modified_at
            plan_orm.modified_by = plan.modified_by
            plan_orm.state = plan.state
            self.db.commit()
