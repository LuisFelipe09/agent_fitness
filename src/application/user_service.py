from typing import Optional
from src.domain.models import User, UserProfile
from src.domain.repositories import UserRepository

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
