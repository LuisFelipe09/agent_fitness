from enum import Enum
from typing import Set


class Role(Enum):
    """User roles in the fitness agent system"""
    CLIENT = "client"
    TRAINER = "trainer"
    NUTRITIONIST = "nutritionist"
    ADMIN = "admin"


class Permission(Enum):
    """Granular permissions for different actions"""
    # User profile management
    VIEW_OWN_PROFILE = "view_own_profile"
    EDIT_OWN_PROFILE = "edit_own_profile"
    
    # Plan viewing
    VIEW_OWN_PLANS = "view_own_plans"
    
    # Trainer permissions
    CREATE_WORKOUT_PLANS = "create_workout_plans"
    VIEW_CLIENT_PROFILES = "view_client_profiles"
    MANAGE_CLIENTS = "manage_clients"
    VIEW_OWN_CLIENTS = "view_own_clients"
    
    # Nutritionist permissions
    CREATE_NUTRITION_PLANS = "create_nutrition_plans"
    
    # Admin permissions
    ASSIGN_ROLES = "assign_roles"
    REMOVE_ROLES = "remove_roles"
    VIEW_ALL_USERS = "view_all_users"
    DELETE_USERS = "delete_users"


# Mapping of roles to their permissions
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.CLIENT: {
        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
        Permission.VIEW_OWN_PLANS,
    },
    Role.TRAINER: {
        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
        Permission.VIEW_OWN_PLANS,
        Permission.CREATE_WORKOUT_PLANS,
        Permission.VIEW_CLIENT_PROFILES,
        Permission.MANAGE_CLIENTS,
        Permission.VIEW_OWN_CLIENTS,
    },
    Role.NUTRITIONIST: {
        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
        Permission.VIEW_OWN_PLANS,
        Permission.CREATE_NUTRITION_PLANS,
        Permission.VIEW_CLIENT_PROFILES,
        Permission.MANAGE_CLIENTS,
        Permission.VIEW_OWN_CLIENTS,
    },
    Role.ADMIN: set(Permission),  # Admins have all permissions
}


def get_permissions_for_roles(roles: list[Role]) -> Set[Permission]:
    """Get all permissions for a list of roles (union of all role permissions)"""
    permissions = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, set()))
    return permissions
