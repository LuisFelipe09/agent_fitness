"""
Unit tests for RoleService using mocks.
"""
import pytest
from unittest.mock import Mock
from src.application.role_service import RoleService
from src.domain.models import User
from src.domain.permissions import Role


class TestRoleServiceAssignment:
    """Tests for role assignment"""
    
    def test_assign_role_success(self, mock_user_repo, sample_user):
        """Test admin successfully assigns a role"""
        # Arrange
        admin = User(id="admin_123", username="admin", roles=["admin"])
        client = User(id="user_123", username="client", roles=["client"])
        
        mock_user_repo.get_by_id.side_effect = [admin, client]
        service = RoleService(mock_user_repo)
        
        # Act
        result = service.assign_role("admin_123", "user_123", "trainer")
        
        # Assert
        assert "trainer" in result.roles
        mock_user_repo.update.assert_called_once()
    
    def test_assign_role_non_admin(self, mock_user_repo):
        """Test non-admin cannot assign roles"""
        # Arrange
        non_admin = User(id="user_123", username="user", roles=["client"])
        mock_user_repo.get_by_id.return_value = non_admin
        service = RoleService(mock_user_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="Only admins can assign roles"):
            service.assign_role("user_123", "other_user", "trainer")
        
        mock_user_repo.update.assert_not_called()
    
    def test_assign_role_user_not_found(self, mock_user_repo):
        """Test assignment fails when target user not found"""
        # Arrange
        admin = User(id="admin_123", username="admin", roles=["admin"])
        mock_user_repo.get_by_id.side_effect = [admin, None]
        service = RoleService(mock_user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            service.assign_role("admin_123", "nonexistent", "trainer")
    
    def test_assign_invalid_role(self, mock_user_repo):
        """Test assignment fails with invalid role"""
        # Arrange
        admin = User(id="admin_123", username="admin", roles=["admin"])
        client = User(id="user_123", username="client", roles=["client"])
        mock_user_repo.get_by_id.side_effect = [admin, client]
        service = RoleService(mock_user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid role"):
            service.assign_role("admin_123", "user_123", "invalid_role")


class TestRoleServiceRemoval:
    """Tests for role removal"""
    
    def test_remove_role_success(self, mock_user_repo):
        """Test admin successfully removes a role"""
        # Arrange
        admin = User(id="admin_123", username="admin", roles=["admin"])
        user_with_multiple_roles = User(
            id="user_123",
            username="user",
            roles=["client", "trainer"]
        )
        mock_user_repo.get_by_id.side_effect = [admin, user_with_multiple_roles]
        service = RoleService(mock_user_repo)
        
        # Act
        result = service.remove_role("admin_123", "user_123", "trainer")
        
        # Assert
        assert "trainer" not in result.roles
        assert "client" in result.roles
        mock_user_repo.update.assert_called_once()
    
    def test_remove_last_role_fails(self, mock_user_repo):
        """Test cannot remove user's last role"""
        # Arrange
        admin = User(id="admin_123", username="admin", roles=["admin"])
        user_with_one_role = User(id="user_123", username="user", roles=["client"])
        mock_user_repo.get_by_id.side_effect = [admin, user_with_one_role]
        service = RoleService(mock_user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="User must have at least one role"):
            service.remove_role("admin_123", "user_123", "client")
        
        mock_user_repo.update.assert_not_called()


class TestRoleServiceProfessionalAssignment:
    """Tests for trainer/nutritionist assignment"""
    
    def test_assign_trainer_success(self, mock_user_repo):
        """Test successful trainer assignment"""
        # Arrange
        trainer = User(id="trainer_123", username="trainer", roles=["trainer"])
        client = User(id="client_123", username="client", roles=["client"])
        mock_user_repo.get_by_id.side_effect = [trainer, client]
        service = RoleService(mock_user_repo)
        
        # Act
        result = service.assign_trainer("client_123", "trainer_123")
        
        # Assert
        assert result.trainer_id == "trainer_123"
        mock_user_repo.update.assert_called_once()
    
    def test_assign_trainer_not_trainer_role(self, mock_user_repo):
        """Test assignment fails when user doesn't have trainer role"""
        # Arrange
        non_trainer = User(id="user_123", username="user", roles=["client"])
        mock_user_repo.get_by_id.return_value = non_trainer
        service = RoleService(mock_user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="User is not a trainer"):
            service.assign_trainer("client_123", "user_123")
    
    def test_assign_nutritionist_success(self, mock_user_repo):
        """Test successful nutritionist assignment"""
        # Arrange
        nutritionist = User(
            id="nutritionist_123",
            username="nutritionist",
            roles=["nutritionist"]
        )
        client = User(id="client_123", username="client", roles=["client"])
        mock_user_repo.get_by_id.side_effect = [nutritionist, client]
        service = RoleService(mock_user_repo)
        
        # Act
        result = service.assign_nutritionist("client_123", "nutritionist_123")
        
        # Assert
        assert result.nutritionist_id == "nutritionist_123"
        mock_user_repo.update.assert_called_once()


class TestRoleServiceClientRetrieval:
    """Tests for client retrieval"""
    
    def test_get_my_clients_as_trainer(self, mock_user_repo):
        """Test trainer gets their clients"""
        # Arrange
        trainer = User(id="trainer_123", username="trainer", roles=["trainer"])
        client1 = User(id="client_1", username="client1", roles=["client"])
        client2 = User(id="client_2", username="client2", roles=["client"])
        
        mock_user_repo.get_by_id.return_value = trainer
        mock_user_repo.get_clients_by_trainer.return_value = [client1, client2]
        service = RoleService(mock_user_repo)
        
        # Act
        result = service.get_my_clients("trainer_123")
        
        # Assert
        assert len(result) == 2
        assert client1 in result
        assert client2 in result
    
    def test_get_my_clients_as_nutritionist(self, mock_user_repo):
        """Test nutritionist gets their clients"""
        # Arrange
        nutritionist = User(
            id="nutritionist_123",
            username="nutritionist",
            roles=["nutritionist"]
        )
        client1 = User(id="client_1", username="client1", roles=["client"])
        
        mock_user_repo.get_by_id.return_value = nutritionist
        mock_user_repo.get_clients_by_nutritionist.return_value = [client1]
        service = RoleService(mock_user_repo)
        
        # Act
        result = service.get_my_clients("nutritionist_123")
        
        # Assert
        assert len(result) == 1
        assert client1 in result


class TestRoleServiceAdminQueries:
    """Tests for admin query functions"""
    
    def test_get_users_by_role_success(self, mock_user_repo):
        """Test admin can get users by role"""
        # Arrange
        admin = User(id="admin_123", username="admin", roles=["admin"])
        trainer1 = User(id="trainer_1", username="trainer1", roles=["trainer"])
        trainer2 = User(id="trainer_2", username="trainer2", roles=["trainer"])
        
        mock_user_repo.get_by_id.return_value = admin
        mock_user_repo.get_by_role.return_value = [trainer1, trainer2]
        service = RoleService(mock_user_repo)
        
        # Act
        result = service.get_users_by_role("admin_123", "trainer")
        
        # Assert
        assert len(result) == 2
        mock_user_repo.get_by_role.assert_called_once_with("trainer")
    
    def test_get_users_by_role_non_admin(self, mock_user_repo):
        """Test non-admin cannot get users by role"""
        # Arrange
        non_admin = User(id="user_123", username="user", roles=["client"])
        mock_user_repo.get_by_id.return_value = non_admin
        service = RoleService(mock_user_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="Only admins can view users by role"):
            service.get_users_by_role("user_123", "trainer")
    
    def test_get_all_users_success(self, mock_user_repo):
        """Test admin can get all users"""
        # Arrange
        admin = User(id="admin_123", username="admin", roles=["admin"])
        all_users = [
            User(id="user_1", username="user1", roles=["client"]),
            User(id="user_2", username="user2", roles=["trainer"]),
        ]
        
        mock_user_repo.get_by_id.return_value = admin
        mock_user_repo.get_all.return_value = all_users
        service = RoleService(mock_user_repo)
        
        # Act
        result = service.get_all_users("admin_123")
        
        # Assert
        assert len(result) == 2
        mock_user_repo.get_all.assert_called_once()
