"""
Unit tests for NotificationService using mocks.
"""
import pytest
from unittest.mock import Mock
from src.application.notification_service import NotificationService
from src.domain.models import Notification, NotificationType
from datetime import datetime


class TestNotificationServiceCreation:
    """Tests for notification creation"""
    
    def test_create_notification_success(self):
        """Test creating a notification"""
        # Arrange
        mock_repo = Mock()
        service = NotificationService(mock_repo)
        
        # Act
        result = service.create_notification(
            user_id="user_123",
            type=NotificationType.PLAN_UPDATED,
            title="Plan Updated",
            message="Your plan has been updated",
            related_entity_type="workout_plan",
            related_entity_id="plan_123"
        )
        
        # Assert
        assert result.user_id == "user_123"
        assert result.type == "plan_updated"
        assert result.title == "Plan Updated"
        assert result.is_read == False
        assert result.related_entity_id == "plan_123"
        mock_repo.save.assert_called_once()
    
    def test_create_notification_string_type(self):
        """Test creating notification with string type"""
        # Arrange
        mock_repo = Mock()
        service = NotificationService(mock_repo)
        
        # Act
        result = service.create_notification(
            user_id="user_123",
            type="plan_created",
            title="Plan Created",
            message="New plan created"
        )
        
        # Assert
        assert result.type == "plan_created"
        mock_repo.save.assert_called_once()


class TestNotificationServiceRetrieval:
    """Tests for notification retrieval"""
    
    def test_get_user_notifications_all(self):
        """Test getting all notifications for a user"""
        # Arrange
        mock_repo = Mock()
        notifications = [
            Notification(
                id="n1",
                user_id="user_123",
                type="plan_updated",
                title="Title 1",
                message="Message 1",
                is_read=False,
                created_at=datetime.now()
            ),
            Notification(
                id="n2",
                user_id="user_123",
                type="plan_created",
                title="Title 2",
                message="Message 2",
                is_read=True,
                created_at=datetime.now()
            )
        ]
        mock_repo.get_by_user_id.return_value = notifications
        service = NotificationService(mock_repo)
        
        # Act
        result = service.get_user_notifications("user_123", unread_only=False)
        
        # Assert
        assert len(result) == 2
        mock_repo.get_by_user_id.assert_called_once_with("user_123", False)
    
    def test_get_user_notifications_unread_only(self):
        """Test getting only unread notifications"""
        # Arrange
        mock_repo = Mock()
        unread_notifications = [
            Notification(
                id="n1",
                user_id="user_123",
                type="plan_updated",
                title="Title 1",
                message="Message 1",
                is_read=False,
                created_at=datetime.now()
            )
        ]
        mock_repo.get_by_user_id.return_value = unread_notifications
        service = NotificationService(mock_repo)
        
        # Act
        result = service.get_user_notifications("user_123", unread_only=True)
        
        # Assert
        assert len(result) == 1
        assert result[0].is_read == False
        mock_repo.get_by_user_id.assert_called_once_with("user_123", True)


class TestNotificationServiceMarkAsRead:
    """Tests for marking notifications as read"""
    
    def test_mark_as_read_success(self):
        """Test marking notification as read"""
        # Arrange
        mock_repo = Mock()
        notification = Notification(
            id="n1",
            user_id="user_123",
            type="plan_updated",
            title="Title",
            message="Message",
            is_read=False,
            created_at=datetime.now()
        )
        mock_repo.get_by_id.return_value = notification
        service = NotificationService(mock_repo)
        
        # Act
        service.mark_as_read("n1", "user_123")
        
        # Assert
        mock_repo.mark_as_read.assert_called_once_with("n1")
    
    def test_mark_as_read_wrong_user(self):
        """Test cannot mark another user's notification as read"""
        # Arrange
        mock_repo = Mock()
        notification = Notification(
            id="n1",
            user_id="user_123",
            type="plan_updated",
            title="Title",
            message="Message",
            is_read=False,
            created_at=datetime.now()
        )
        mock_repo.get_by_id.return_value = notification
        service = NotificationService(mock_repo)
        
        # Act
        service.mark_as_read("n1", "different_user")
        
        # Assert - should not mark as read
        mock_repo.mark_as_read.assert_not_called()
    
    def test_mark_as_read_not_found(self):
        """Test marking non-existent notification as read"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        service = NotificationService(mock_repo)
        
        # Act
        service.mark_as_read("n1", "user_123")
        
        # Assert
        mock_repo.mark_as_read.assert_not_called()
    
    def test_mark_all_read_success(self):
        """Test marking all notifications as read for a user"""
        # Arrange
        mock_repo = Mock()
        service = NotificationService(mock_repo)
        
        # Act
        service.mark_all_read("user_123")
        
        # Assert
        mock_repo.mark_all_as_read.assert_called_once_with("user_123")
