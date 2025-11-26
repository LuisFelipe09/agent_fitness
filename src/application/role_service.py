from typing import List, Optional
from src.domain.models import User
from src.domain.permissions import Role
from src.domain.repositories import UserRepository


class RoleService:
    """Service for managing user roles and assignments"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def assign_role(self, admin_id: str, user_id: str, role: str) -> User:
        """Admin assigns a role to a user
        
        Args:
            admin_id: ID of the admin performing the action
            user_id: ID of the user receiving the role
            role: Role to assign (as string or Role enum)
            
        Returns:
            Updated user
            
        Raises:
            PermissionError: If admin doesn't have permission
            ValueError: If user not found or invalid role
        """
        # Verify admin has permission
        admin = self.user_repo.get_by_id(admin_id)
        if not admin or not admin.has_role(Role.ADMIN.value):
            raise PermissionError("Only admins can assign roles")
        
        # Get target user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Validate and normalize role
        if isinstance(role, Role):
            role = role.value
        
        # Validate role exists
        try:
            Role(role)
        except ValueError:
            raise ValueError(f"Invalid role: {role}")
        
        # Add role if not already present
        if role not in user.roles:
            user.roles.append(role)
            self.user_repo.update(user)
        
        return user
    
    def remove_role(self, admin_id: str, user_id: str, role: str) -> User:
        """Admin removes a role from a user
        
        Args:
            admin_id: ID of the admin performing the action
            user_id: ID of the user losing the role
            role: Role to remove
            
        Returns:
            Updated user
            
        Raises:
            PermissionError: If admin doesn't have permission
            ValueError: If user not found or trying to remove last role
        """
        # Verify admin has permission
        admin = self.user_repo.get_by_id(admin_id)
        if not admin or not admin.has_role(Role.ADMIN.value):
            raise PermissionError("Only admins can remove roles")
        
        # Get target user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Normalize role
        if isinstance(role, Role):
            role = role.value
        
        # Remove role if present
        if role in user.roles:
            # Ensure user has at least one role
            if len(user.roles) <= 1:
                raise ValueError("User must have at least one role")
            
            user.roles.remove(role)
            self.user_repo.update(user)
        
        return user
    
    def assign_trainer(self, client_id: str, trainer_id: str) -> User:
        """Assign a trainer to a client
        
        Args:
            client_id: ID of the client
            trainer_id: ID of the trainer
            
        Returns:
            Updated client user
            
        Raises:
            ValueError: If trainer/client not found or trainer doesn't have TRAINER role
        """
        # Verify trainer exists and has TRAINER role
        trainer = self.user_repo.get_by_id(trainer_id)
        if not trainer:
            raise ValueError("Trainer not found")
        
        if not trainer.has_role(Role.TRAINER.value):
            raise ValueError("User is not a trainer")
        
        # Get client
        client = self.user_repo.get_by_id(client_id)
        if not client:
            raise ValueError("Client not found")
        
        # Assign trainer
        client.trainer_id = trainer_id
        self.user_repo.update(client)
        return client
    
    def assign_nutritionist(self, client_id: str, nutritionist_id: str) -> User:
        """Assign a nutritionist to a client
        
        Args:
            client_id: ID of the client
            nutritionist_id: ID of the nutritionist
            
        Returns:
            Updated client user
            
        Raises:
            ValueError: If nutritionist/client not found or nutritionist doesn't have NUTRITIONIST role
        """
        # Verify nutritionist exists and has NUTRITIONIST role
        nutritionist = self.user_repo.get_by_id(nutritionist_id)
        if not nutritionist:
            raise ValueError("Nutritionist not found")
        
        if not nutritionist.has_role(Role.NUTRITIONIST.value):
            raise ValueError("User is not a nutritionist")
        
        # Get client
        client = self.user_repo.get_by_id(client_id)
        if not client:
            raise ValueError("Client not found")
        
        # Assign nutritionist
        client.nutritionist_id = nutritionist_id
        self.user_repo.update(client)
        return client
    
    def get_my_clients(self, professional_id: str) -> List[User]:
        """Get all clients assigned to a trainer or nutritionist
        
        Args:
            professional_id: ID of the trainer/nutritionist
            
        Returns:
            List of client users
        """
        professional = self.user_repo.get_by_id(professional_id)
        if not professional:
            return []
        
        clients = []
        
        # Get clients if user is a trainer
        if professional.has_role(Role.TRAINER.value):
            clients.extend(self.user_repo.get_clients_by_trainer(professional_id))
        
        # Get clients if user is a nutritionist
        if professional.has_role(Role.NUTRITIONIST.value):
            nutritionist_clients = self.user_repo.get_clients_by_nutritionist(professional_id)
            # Avoid duplicates if user is both trainer and nutritionist for same client
            for client in nutritionist_clients:
                if client not in clients:
                    clients.append(client)
        
        return clients
    
    def get_users_by_role(self, admin_id: str, role: str) -> List[User]:
        """Get all users with a specific role (admin only)
        
        Args:
            admin_id: ID of the admin requesting the list
            role: Role to filter by
            
        Returns:
            List of users with the specified role
            
        Raises:
            PermissionError: If user is not an admin
        """
        admin = self.user_repo.get_by_id(admin_id)
        if not admin or not admin.has_role(Role.ADMIN.value):
            raise PermissionError("Only admins can view users by role")
        
        # Normalize role
        if isinstance(role, Role):
            role = role.value
        
        return self.user_repo.get_by_role(role)
    
    def get_all_users(self, admin_id: str) -> List[User]:
        """Get all users in the system (admin only)
        
        Args:
            admin_id: ID of the admin requesting the list
            
        Returns:
            List of all users
            
        Raises:
            PermissionError: If user is not an admin
        """
        admin = self.user_repo.get_by_id(admin_id)
        if not admin or not admin.has_role(Role.ADMIN.value):
            raise PermissionError("Only admins can view all users")
        
        return self.user_repo.get_all()
