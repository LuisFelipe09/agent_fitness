from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import User, UserProfile, Goal, ActivityLevel
from src.domain.repositories import CompleteUserRepository
from src.infrastructure.orm_models import UserORM
from dataclasses import asdict

class SqlAlchemyUserRepository(CompleteUserRepository):
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
            password_hash=user_orm.password_hash,
            email=user_orm.email,
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
            password_hash=user.password_hash,
            email=user.email,
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
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        user_orm = self.db.query(UserORM).filter(UserORM.username == username).first()
        if not user_orm:
            return None
        return self.get_by_id(user_orm.id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_orm = self.db.query(UserORM).filter(UserORM.email == email).first()
        if not user_orm:
            return None
        return self.get_by_id(user_orm.id)
