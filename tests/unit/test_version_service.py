"""
Unit tests for VersionService using mocks.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime
from src.application.version_service import VersionService
from src.domain.models import PlanVersion, WorkoutPlan, NutritionPlan


class TestVersionServiceCreation:
    """Tests for version creation"""
    
    def test_create_version_workout_plan(self, sample_workout_plan):
        """Test creating version for workout plan"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_plan_id.return_value = []  # No previous versions
        service = VersionService(mock_repo)
        
        # Act
        result = service.create_version(
            sample_workout_plan,
            changed_by="trainer_123",
            summary="Initial version"
        )
        
        # Assert
        assert result.plan_id == sample_workout_plan.id
        assert result.plan_type == "workout"
        assert result.version_number == 1
        assert result.created_by == "trainer_123"
        assert result.changes_summary == "Initial version"
        assert result.state_at_version == "draft"
        mock_repo.save.assert_called_once()
    
    def test_create_version_nutrition_plan(self, sample_nutrition_plan):
        """Test creating version for nutrition plan"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_plan_id.return_value = []
        service = VersionService(mock_repo)
        
        # Act
        result = service.create_version(
            sample_nutrition_plan,
            changed_by="nutritionist_123",
            summary="Initial version"
        )
        
        # Assert
        assert result.plan_type == "nutrition"
        assert result.version_number == 1
        mock_repo.save.assert_called_once()
    
    def test_create_version_increments_number(self, sample_workout_plan):
        """Test version number increments with existing versions"""
        # Arrange
        mock_repo = Mock()
        existing_versions = [
            PlanVersion(
                id="v1",
                plan_id=sample_workout_plan.id,
                plan_type="workout",
                version_number=1,
                created_by="user",
                created_at=datetime.now(),
                changes_summary="First",
                data_snapshot={},
                state_at_version="draft"
            ),
            PlanVersion(
                id="v2",
                plan_id=sample_workout_plan.id,
                plan_type="workout",
                version_number=2,
                created_by="user",
                created_at=datetime.now(),
                changes_summary="Second",
                data_snapshot={},
                state_at_version="approved"
            )
        ]
        mock_repo.get_by_plan_id.return_value = existing_versions
        service = VersionService(mock_repo)
        
        # Act
        result = service.create_version(
            sample_workout_plan,
            changed_by="trainer_123",
            summary="Third version"
        )
        
        # Assert
        assert result.version_number == 3


class TestVersionServiceHistory:
    """Tests for version history retrieval"""
    
    def test_get_history_success(self):
        """Test getting version history"""
        # Arrange
        mock_repo = Mock()
        versions = [
            PlanVersion(
                id="v1",
                plan_id="plan_123",
                plan_type="workout",
                version_number=1,
                created_by="user",
                created_at=datetime.now(),
                changes_summary="V1",
                data_snapshot={},
                state_at_version="draft"
            )
        ]
        mock_repo.get_by_plan_id.return_value = versions
        service = VersionService(mock_repo)
        
        # Act
        result = service.get_history("plan_123")
        
        # Assert
        assert len(result) == 1
        assert result[0].version_number == 1
        mock_repo.get_by_plan_id.assert_called_once_with("plan_123")
    
    def test_get_history_empty(self):
        """Test getting history for plan with no versions"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_plan_id.return_value = []
        service = VersionService(mock_repo)
        
        # Act
        result = service.get_history("plan_123")
        
        # Assert
        assert len(result) == 0
