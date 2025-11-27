"""
Authentication and role-related Data Transfer Objects (DTOs).

These DTOs handle role assignments and professional assignments.
"""
from pydantic import BaseModel

class RoleAssignmentRequest(BaseModel):
    """Request model for assigning a role to a user"""
    role: str

class ProfessionalAssignmentRequest(BaseModel):
    """Request model for assigning a trainer or nutritionist to a client"""
    professional_id: str
