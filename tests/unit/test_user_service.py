"""
Unit tests for UserService using mocks.
"""
import pytest
from unittest.mock import Mock
from src.application.user_service import UserService
from src.domain.models import User, UserProfile, Goal, ActivityLevel


class TestUserServiceRegistration:
    """Tests for user registration"""
    
    def test_register_new_user(self, mock_user_repo):
        """Test registering a new user"""
        # Arrange
        mock_user_repo.get_by_id.return_value = None
        service = UserService(mock_user_repo)
        
        # Act
        result = service.register_user("user_123", "test_user")
        
        # Assert
        assert result.id == "user_123"
        assert result.username == "test_user"
        mock_user_repo.save.assert_called_once()
    
    def test_register_existing_user(self, mock_user_repo, sample_user):
        """Test registering an existing user returns existing user"""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user
        service = UserService(mock_user_repo)
        
        # Act
        result = service.register_user("user_123", "test_user")
        
        # Assert
        assert result == sample_user
        mock_user_repo.save.assert_not_called()


class TestUserServiceProfileUpdate:
    """Tests for user profile updates"""
    
    def test_update_profile_success(self, mock_user_repo, sample_user):
        """Test successful profile update"""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user
        service = UserService(mock_user_repo)
        
        new_profile = UserProfile(
            age=35,
            weight=85.0,
            height=180.0,
            gender="Male",
            goal=Goal.WEIGHT_LOSS,
            activity_level=ActivityLevel.VERY_ACTIVE,
            dietary_restrictions=["gluten"],
            injuries=[]
        )
        
        # Act
        result = service.update_profile("user_123", new_profile)
        
        # Assert
        assert result.profile == new_profile
        assert result.profile.age == 35
        assert result.profile.weight == 85.0
        mock_user_repo.update.assert_called_once()
    
    def test_update_profile_user_not_found(self, mock_user_repo):
        """Test profile update fails when user doesn't exist"""
        # Arrange
        mock_user_repo.get_by_id.return_value = None
        service = UserService(mock_user_repo)
        
        new_profile = UserProfile(
            age=35,
            weight=85.0,
            height=180.0,
            gender="Male",
            goal=Goal.WEIGHT_LOSS,
            activity_level=ActivityLevel.VERY_ACTIVE
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            service.update_profile("user_123", new_profile)
        
        mock_user_repo.update.assert_not_called()


class TestUserServiceRetrieval:
    """Tests for user retrieval"""
    
    def test_get_user_success(self, mock_user_repo, sample_user):
        """Test getting an existing user"""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user
        service = UserService(mock_user_repo)
        
        # Act
        result = service.get_user("user_123")
        
        # Assert
        assert result == sample_user
        mock_user_repo.get_by_id.assert_called_once_with("user_123")
    
    def test_get_user_not_found(self, mock_user_repo):
        """Test getting a non-existent user returns None"""
        # Arrange
        mock_user_repo.get_by_id.return_value = None
        service = UserService(mock_user_repo)
        
        # Act
        result = service.get_user("user_123")
        
        # Assert
        assert result is None
        mock_user_repo.get_by_id.assert_called_once_with("user_123")
