"""Authentication and authorization utilities for the API"""

from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from src.domain.repositories import UserRepository
from src.dependencies import get_user_repository
from src.domain.models import User
from src.domain.permissions import Role, Permission
from src.interfaces.api.security import decode_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """Get the current authenticated user.
    
    Supports two authentication methods:
    1. JWT token in Authorization header (for web/admin panel)
    2. Telegram user ID in X-User-Id header (for Telegram Mini App)
    
    Args:
        credentials: Bearer token from Authorization header
        x_user_id: User ID from X-User-Id header (Telegram)
        user_repo: User repository
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    user_id = None
    
    # Try JWT authentication first
    if credentials:
        try:
            token_data = decode_token(credentials.credentials)
            user_id = token_data.get("sub")
        except HTTPException:
            # Invalid JWT, try Telegram auth
            pass
    
    # Fallback to Telegram auth
    if not user_id and x_user_id:
        user_id = x_user_id
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide JWT token or X-User-Id header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_repo.get_by_id(user_id)
    
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
