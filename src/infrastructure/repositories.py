from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import User, WorkoutPlan, NutritionPlan, WorkoutSession, Exercise, DailyMealPlan, Meal, PlanVersion, PlanComment, Notification, UserProfile, Goal, ActivityLevel
from src.domain.repositories import UserRepository, WorkoutPlanRepository, NutritionPlanRepository, PlanVersionRepository, PlanCommentRepository, NotificationRepository
from .orm_models import UserORM, WorkoutPlanORM, NutritionPlanORM, PlanVersionORM, PlanCommentORM, NotificationORM
from dataclasses import asdict

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        user_orm = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user_orm:
            return None
        
        profile = None
        if user_orm.profile_data:
            data = user_orm.profile_data
            profile = UserProfile(
                age=data['age'],
                weight=data['weight'],
                height=data['height'],
                gender=data['gender'],
                goal=Goal(data['goal']),
                activity_level=ActivityLevel(data['activity_level']),
                dietary_restrictions=data.get('dietary_restrictions', []),
                injuries=data.get('injuries', [])
            )

        return User(
            id=user_orm.id,
            username=user_orm.username,
            roles=user_orm.roles if user_orm.roles else ["client"],
            profile=profile,
            created_at=user_orm.created_at,
            trainer_id=user_orm.trainer_id,
            nutritionist_id=user_orm.nutritionist_id
        )

    def save(self, user: User) -> None:
        profile_data = None
        if user.profile:
            profile_data = asdict(user.profile)
            # Convert Enums to values for JSON serialization
            profile_data['goal'] = user.profile.goal.value
            profile_data['activity_level'] = user.profile.activity_level.value

        user_orm = UserORM(
            id=user.id,
            username=user.username,
            roles=user.roles,
            profile_data=profile_data,
            created_at=user.created_at,
            trainer_id=user.trainer_id,
            nutritionist_id=user.nutritionist_id
        )
        self.db.add(user_orm)
        self.db.commit()

    def update(self, user: User) -> None:
        user_orm = self.db.query(UserORM).filter(UserORM.id == user.id).first()
        if user_orm:
            profile_data = None
            if user.profile:
                profile_data = asdict(user.profile)
                profile_data['goal'] = user.profile.goal.value
                profile_data['activity_level'] = user.profile.activity_level.value
            
            user_orm.roles = user.roles
            user_orm.profile_data = profile_data
            user_orm.trainer_id = user.trainer_id
            user_orm.nutritionist_id = user.nutritionist_id
            self.db.commit()
    
    def get_by_role(self, role: str) -> list[User]:
        """Get all users with a specific role"""
        # Query users where the roles JSON array contains the role
        users_orm = self.db.query(UserORM).all()
        users = []
        for user_orm in users_orm:
            if user_orm.roles and role in user_orm.roles:
                user = self.get_by_id(user_orm.id)
                if user:
                    users.append(user)
        return users
    
    def get_all(self) -> list[User]:
        """Get all users (admin only)"""
        users_orm = self.db.query(UserORM).all()
        users = []
        for user_orm in users_orm:
            user = self.get_by_id(user_orm.id)
            if user:
                users.append(user)
        return users
    
    def get_clients_by_trainer(self, trainer_id: str) -> list[User]:
        """Get all clients assigned to a specific trainer"""
        users_orm = self.db.query(UserORM).filter(UserORM.trainer_id == trainer_id).all()
        users = []
        for user_orm in users_orm:
            user = self.get_by_id(user_orm.id)
            if user:
                users.append(user)
        return users
    
    def get_clients_by_nutritionist(self, nutritionist_id: str) -> list[User]:
        """Get all clients assigned to a specific nutritionist"""
        users_orm = self.db.query(UserORM).filter(UserORM.nutritionist_id == nutritionist_id).all()
        users = []
        for user_orm in users_orm:
            user = self.get_by_id(user_orm.id)
            if user:
                users.append(user)
        return users

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
            state=plan_orm.state if plan_orm.state else "draft"
        )

    def save(self, plan: NutritionPlan) -> None:
        daily_plans_data = [asdict(d) for d in plan.daily_plans]
        
        plan_orm = NutritionPlanORM(
            id=plan.id,
            user_id=plan.user_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            created_at=plan.created_at,
            daily_plans_data=daily_plans_data,
            created_by=plan.created_by,
            modified_at=plan.modified_at,
            modified_by=plan.modified_by,
            state=plan.state
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
            state=plan_orm.state if plan_orm.state else "draft"
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
            self.db.commit()

class SqlAlchemyPlanVersionRepository(PlanVersionRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, version: PlanVersion) -> None:
        version_orm = PlanVersionORM(
            id=version.id,
            plan_id=version.plan_id,
            plan_type=version.plan_type,
            version_number=version.version_number,
            created_by=version.created_by,
            created_at=version.created_at,
            changes_summary=version.changes_summary,
            data_snapshot=version.data_snapshot,
            state_at_version=version.state_at_version
        )
        self.db.add(version_orm)
        self.db.commit()
    
    def get_by_plan_id(self, plan_id: str) -> List[PlanVersion]:
        versions_orm = self.db.query(PlanVersionORM).filter(PlanVersionORM.plan_id == plan_id).order_by(PlanVersionORM.version_number.desc()).all()
        return [
            PlanVersion(
                id=v.id,
                plan_id=v.plan_id,
                plan_type=v.plan_type,
                version_number=v.version_number,
                created_by=v.created_by,
                created_at=v.created_at,
                changes_summary=v.changes_summary,
                data_snapshot=v.data_snapshot,
                state_at_version=v.state_at_version
            )
            for v in versions_orm
        ]
    
    def get_by_id(self, version_id: str) -> Optional[PlanVersion]:
        v = self.db.query(PlanVersionORM).filter(PlanVersionORM.id == version_id).first()
        if not v:
            return None
        return PlanVersion(
            id=v.id,
            plan_id=v.plan_id,
            plan_type=v.plan_type,
            version_number=v.version_number,
            created_by=v.created_by,
            created_at=v.created_at,
            changes_summary=v.changes_summary,
            data_snapshot=v.data_snapshot,
            state_at_version=v.state_at_version
        )

class SqlAlchemyPlanCommentRepository(PlanCommentRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, comment: PlanComment) -> None:
        comment_orm = PlanCommentORM(
            id=comment.id,
            plan_id=comment.plan_id,
            plan_type=comment.plan_type,
            author_id=comment.author_id,
            author_role=comment.author_role,
            content=comment.content,
            created_at=comment.created_at,
            edited_at=comment.edited_at,
            is_internal=comment.is_internal
        )
        self.db.merge(comment_orm)  # Use merge to handle both insert and update
        self.db.commit()
    
    def get_by_plan_id(self, plan_id: str) -> List[PlanComment]:
        comments_orm = self.db.query(PlanCommentORM).filter(PlanCommentORM.plan_id == plan_id).order_by(PlanCommentORM.created_at.asc()).all()
        return [
            PlanComment(
                id=c.id,
                plan_id=c.plan_id,
                plan_type=c.plan_type,
                author_id=c.author_id,
                author_role=c.author_role,
                content=c.content,
                created_at=c.created_at,
                edited_at=c.edited_at,
                is_internal=c.is_internal
            )
            for c in comments_orm
        ]
    
    def get_by_id(self, comment_id: str) -> Optional[PlanComment]:
        c = self.db.query(PlanCommentORM).filter(PlanCommentORM.id == comment_id).first()
        if not c:
            return None
        return PlanComment(
            id=c.id,
            plan_id=c.plan_id,
            plan_type=c.plan_type,
            author_id=c.author_id,
            author_role=c.author_role,
            content=c.content,
            created_at=c.created_at,
            edited_at=c.edited_at,
            is_internal=c.is_internal
        )
    
    def delete(self, comment_id: str) -> None:
        self.db.query(PlanCommentORM).filter(PlanCommentORM.id == comment_id).delete()
        self.db.commit()

class SqlAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, notification: Notification) -> None:
        notification_orm = NotificationORM(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            related_entity_type=notification.related_entity_type,
            related_entity_id=notification.related_entity_id,
            is_read=notification.is_read,
            created_at=notification.created_at,
            read_at=notification.read_at
        )
        self.db.merge(notification_orm)
        self.db.commit()
    
    def get_by_user_id(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        query = self.db.query(NotificationORM).filter(NotificationORM.user_id == user_id)
        if unread_only:
            query = query.filter(NotificationORM.is_read == False)
        
        notifications_orm = query.order_by(NotificationORM.created_at.desc()).all()
        return [
            Notification(
                id=n.id,
                user_id=n.user_id,
                type=n.type,
                title=n.title,
                message=n.message,
                related_entity_type=n.related_entity_type,
                related_entity_id=n.related_entity_id,
                is_read=n.is_read,
                created_at=n.created_at,
                read_at=n.read_at
            )
            for n in notifications_orm
        ]
    
    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        n = self.db.query(NotificationORM).filter(NotificationORM.id == notification_id).first()
        if not n:
            return None
        return Notification(
            id=n.id,
            user_id=n.user_id,
            type=n.type,
            title=n.title,
            message=n.message,
            related_entity_type=n.related_entity_type,
            related_entity_id=n.related_entity_id,
            is_read=n.is_read,
            created_at=n.created_at,
            read_at=n.read_at
        )
    
    def mark_as_read(self, notification_id: str) -> None:
        from datetime import datetime
        self.db.query(NotificationORM).filter(NotificationORM.id == notification_id).update(
            {"is_read": True, "read_at": datetime.now()}
        )
        self.db.commit()
    
    def mark_all_as_read(self, user_id: str) -> None:
        from datetime import datetime
        self.db.query(NotificationORM).filter(NotificationORM.user_id == user_id, NotificationORM.is_read == False).update(
            {"is_read": True, "read_at": datetime.now()}
        )
        self.db.commit()
