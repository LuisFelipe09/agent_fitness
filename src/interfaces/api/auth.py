"""Authentication and authorization utilities for the API"""

from fastapi import HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from src.infrastructure.database import get_db
from src.infrastructure.repositories import SqlAlchemyUserRepository
from src.domain.permissions import Role, Permission
from src.domain.models import User


def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """Extract user ID from request header
    
    In a production app, this would validate JWT tokens or session cookies.
    For the MVP with Telegram Mini App, we use a simple header.
    
    Args:
        x_user_id: User ID from X-User-Id header
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If user ID not provided
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401, 
            detail="Authentication required. X-User-Id header missing."
        )
    return x_user_id


def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user
    
    Args:
        user_id: User ID from header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user not found
    """
    repo = SqlAlchemyUserRepository(db)
    user = repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


def require_role(*required_roles: Role):
    """Dependency to require one or more specific roles
    
    Args:
        *required_roles: One or more Role enums that the user must have
        
    Returns:
        Dependency function that validates the user has at least one of the required roles
        
    Example:
        @router.get("/admin/users", dependencies=[Depends(require_role(Role.ADMIN))])
    """
    def dependency(user: User = Depends(get_current_user)) -> User:
        # Check if user has at least one of the required roles
        for role in required_roles:
            if user.has_role(role.value):
                return user
        
        # User doesn't have any of the required roles
        roles_str = ", ".join(r.value for r in required_roles)
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden. Requires one of the following roles: {roles_str}"
        )
    
    return dependency


def require_permission(*required_permissions: Permission):
    """Dependency to require one or more specific permissions
    
    Args:
        *required_permissions: One or more Permission enums that the user must have
        
    Returns:
        Dependency function that validates the user has at least one of the required permissions
        
    Example:
        @router.post("/plans", dependencies=[Depends(require_permission(Permission.CREATE_WORKOUT_PLANS))])
    """
    def dependency(user: User = Depends(get_current_user)) -> User:
        # Check if user has at least one of the required permissions
        for permission in required_permissions:
            if user.has_permission(permission):
                return user
        
        # User doesn't have any of the required permissions
        perms_str = ", ".join(p.value for p in required_permissions)
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden. Requires one of the following permissions: {perms_str}"
        )
    
    return dependency


def is_admin(user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role
    
    Convenience wrapper around require_role(Role.ADMIN)
    """
    if not user.has_role(Role.ADMIN.value):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def is_trainer(user: User = Depends(get_current_user)) -> User:
    """Dependency to require trainer role"""
    if not user.has_role(Role.TRAINER.value):
        raise HTTPException(status_code=403, detail="Trainer access required")
    return user


def is_nutritionist(user: User = Depends(get_current_user)) -> User:
    """Dependency to require nutritionist role"""
    if not user.has_role(Role.NUTRITIONIST.value):
        raise HTTPException(status_code=403, detail="Nutritionist access required")
    return user
