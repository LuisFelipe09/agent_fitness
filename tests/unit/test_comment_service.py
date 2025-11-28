"""
Unit tests for CommentService using mocks.
"""
import pytest
from unittest.mock import Mock
from src.application.comment_service import CommentService
from src.domain.models import PlanComment
from datetime import datetime


class TestCommentServiceCreation:
    """Tests for comment creation"""
    
    def test_add_comment_success(self):
        """Test adding a comment to a plan"""
        # Arrange
        mock_repo = Mock()
        service = CommentService(mock_repo)
        
        # Act
        result = service.add_comment(
            plan_id="plan_123",
            plan_type="workout",
            author_id="user_123",
            author_role="client",
            content="Great plan!",
            is_internal=False
        )
        
        # Assert
        assert result.plan_id == "plan_123"
        assert result.author_id == "user_123"
        assert result.content == "Great plan!"
        assert result.is_internal == False
        mock_repo.save.assert_called_once()
    
    def test_add_internal_comment(self):
        """Test adding an internal comment"""
        # Arrange
        mock_repo = Mock()
        service = CommentService(mock_repo)
        
        # Act
        result = service.add_comment(
            plan_id="plan_123",
            plan_type="workout",
            author_id="trainer_123",
            author_role="trainer",
            content="Internal note",
            is_internal=True
        )
        
        # Assert
        assert result.is_internal == True
        mock_repo.save.assert_called_once()


class TestCommentServiceRetrieval:
    """Tests for comment retrieval"""
    
    def test_get_plan_comments_as_client(self):
        """Test client doesn't see internal comments"""
        # Arrange
        mock_repo = Mock()
        all_comments = [
            PlanComment(
                id="c1",
                plan_id="plan_123",
                plan_type="workout",
                author_id="client_123",
                author_role="client",
                content="Public comment",
                is_internal=False,
                created_at=datetime.now()
            ),
            PlanComment(
                id="c2",
                plan_id="plan_123",
                plan_type="workout",
                author_id="trainer_123",
                author_role="trainer",
                content="Internal note",
                is_internal=True,
                created_at=datetime.now()
            )
        ]
        mock_repo.get_by_plan_id.return_value = all_comments
        service = CommentService(mock_repo)
        
        # Act
        result = service.get_plan_comments("plan_123", user_role="client")
        
        # Assert
        assert len(result) == 1
        assert result[0].content == "Public comment"
    
    def test_get_plan_comments_as_trainer(self):
        """Test trainer sees all comments including internal"""
        # Arrange
        mock_repo = Mock()
        all_comments = [
            PlanComment(
                id="c1",
                plan_id="plan_123",
                plan_type="workout",
                author_id="client_123",
                author_role="client",
                content="Public comment",
                is_internal=False,
                created_at=datetime.now()
            ),
            PlanComment(
                id="c2",
                plan_id="plan_123",
                plan_type="workout",
                author_id="trainer_123",
                author_role="trainer",
                content="Internal note",
                is_internal=True,
                created_at=datetime.now()
            )
        ]
        mock_repo.get_by_plan_id.return_value = all_comments
        service = CommentService(mock_repo)
        
        # Act
        result = service.get_plan_comments("plan_123", user_role="trainer")
        
        # Assert
        assert len(result) == 2


class TestCommentServiceDeletion:
    """Tests for comment deletion"""
    
    def test_delete_comment_success(self):
        """Test author can delete their own comment"""
        # Arrange
        mock_repo = Mock()
        comment = PlanComment(
            id="c1",
            plan_id="plan_123",
            plan_type="workout",
            author_id="user_123",
            author_role="client",
            content="My comment",
            is_internal=False,
            created_at=datetime.now()
        )
        mock_repo.get_by_id.return_value = comment
        service = CommentService(mock_repo)
        
        # Act
        result = service.delete_comment("c1", "user_123")
        
        # Assert
        assert result == True
        mock_repo.delete.assert_called_once_with("c1")
    
    def test_delete_comment_unauthorized(self):
        """Test user cannot delete someone else's comment"""
        # Arrange
        mock_repo = Mock()
        comment = PlanComment(
            id="c1",
            plan_id="plan_123",
            plan_type="workout",
            author_id="user_123",
            author_role="client",
            content="Their comment",
            is_internal=False,
            created_at=datetime.now()
        )
        mock_repo.get_by_id.return_value = comment
        service = CommentService(mock_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="You can only delete your own comments"):
            service.delete_comment("c1", "different_user")
        
        mock_repo.delete.assert_not_called()
    
    def test_delete_comment_not_found(self):
        """Test deleting non-existent comment returns False"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        service = CommentService(mock_repo)
        
        # Act
        result = service.delete_comment("c1", "user_123")
        
        # Assert
        assert result == False
        mock_repo.delete.assert_not_called()
