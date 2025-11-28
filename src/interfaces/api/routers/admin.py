from fastapi import APIRouter, Depends, HTTPException
from src.dependencies import get_role_service
from src.application.role_service import RoleService
from src.domain.models import User
from src.domain.permissions import Role
from src.interfaces.api.auth import get_current_user, require_role
from src.interfaces.api.dto import RoleAssignmentRequest

router = APIRouter()

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.get("/admin/users", dependencies=[Depends(require_role(Role.ADMIN))])
def list_all_users(
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """List all users in the system (admin only)"""
    return service.get_all_users(current_user.id)

@router.get("/admin/users/role/{role}", dependencies=[Depends(require_role(Role.ADMIN))])
def list_users_by_role(
    role: str,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """List all users with a specific role (admin only)"""
    try:
        return service.get_users_by_role(current_user.id, role)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/admin/users/{user_id}/roles", dependencies=[Depends(require_role(Role.ADMIN))])
def assign_role_to_user(
    user_id: str,
    role_data: RoleAssignmentRequest,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """Assign a role to a user (admin only)"""
    try:
        return service.assign_role(current_user.id, user_id, role_data.role)
    except (PermissionError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/admin/users/{user_id}/roles/{role}", dependencies=[Depends(require_role(Role.ADMIN))])
def remove_role_from_user(
    user_id: str,
    role: str,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """Remove a role from a user (admin only)"""
    try:
        return service.remove_role(current_user.id, user_id, role)
    except (PermissionError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
