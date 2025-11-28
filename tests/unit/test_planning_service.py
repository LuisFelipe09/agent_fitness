"""
Unit tests for PlanningService using mocks.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.application.planning_service import PlanningService
from src.domain.models import WorkoutPlan, NutritionPlan


class TestPlanningServiceWorkoutGeneration:
    """Tests for workout plan generation"""
    
    def test_generate_workout_plan_success(
        self,
        mock_ai_service,
        mock_workout_repo,
        mock_nutrition_repo,
        mock_user_repo,
        sample_user,
        sample_workout_plan
    ):
        """Test successful workout plan generation"""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user
        mock_ai_service.generate_workout_plan.return_value = {
            "sessions": [
                {
                    "day": "Monday",
                    "focus": "Chest",
                    "exercises": [
                        {
                            "name": "Bench Press",
                            "description": "Press the bar",
                            "sets": 3,
                            "reps": "10",
                            "rest_time": "60s"
                        }
                    ]
                }
            ]
        }
        
        service = PlanningService(
            mock_ai_service,
            mock_workout_repo,
            mock_nutrition_repo,
            mock_user_repo
        )
        
        # Act
        result = service.generate_workout_plan("user_123")
        
        # Assert
        assert result is not None
        assert result.user_id == "user_123"
        assert len(result.sessions) == 1
        assert result.sessions[0].day == "Monday"
        assert result.sessions[0].focus == "Chest"
        mock_workout_repo.save.assert_called_once()
        mock_ai_service.generate_workout_plan.assert_called_once()
    
    def test_generate_workout_plan_no_profile(
        self,
        mock_ai_service,
        mock_workout_repo,
        mock_nutrition_repo,
        mock_user_repo
    ):
        """Test workout generation fails when user has no profile"""
        # Arrange
        user_without_profile = Mock()
        user_without_profile.id = "user_123"
        user_without_profile.profile = None
        
        mock_user_repo.get_by_id.return_value = user_without_profile
        
        service = PlanningService(
            mock_ai_service,
            mock_workout_repo,
            mock_nutrition_repo,
            mock_user_repo
        )
        
        with pytest.raises(ValueError, match="User profile incomplete or not found"):
            service.generate_workout_plan("user_123")
        
        mock_ai_service.generate_workout_plan.assert_not_called()
        mock_workout_repo.save.assert_not_called()
    
    def test_generate_workout_plan_ai_failure(
        self,
        mock_ai_service,
        mock_workout_repo,
        mock_nutrition_repo,
        mock_user_repo,
        sample_user
    ):
        """Test workout generation handles AI service failure"""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user
        mock_ai_service.generate_workout_plan.side_effect = ValueError("AI service down")
        
        service = PlanningService(
            mock_ai_service,
            mock_workout_repo,
            mock_nutrition_repo,
            mock_user_repo
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="AI service down"):
            service.generate_workout_plan("user_123")
        
        mock_workout_repo.save.assert_not_called()


class TestPlanningServiceWorkoutActivation:
    """Tests for workout plan activation"""
    
    def test_activate_workout_plan_success(
        self,
        mock_ai_service,
        mock_workout_repo,
        mock_nutrition_repo,
        mock_user_repo
    ):
        """Test successful plan activation"""
        # Arrange
        approved_plan = WorkoutPlan(
            id="plan_123",
            user_id="user_123",
            start_date=datetime.now(),
            end_date=datetime.now(),
            sessions=[],
            created_at=datetime.now(),
            state="approved"  # Plan must be approved to activate
        )
        mock_workout_repo.get_by_id.return_value = approved_plan
        
        service = PlanningService(
            mock_ai_service,
            mock_workout_repo,
            mock_nutrition_repo,
            mock_user_repo
        )
        
        # Act
        result = service.activate_workout_plan("plan_123", "user_123")
        
        # Assert
        assert result.state == "active"
        mock_workout_repo.update.assert_called_once()
    
    def test_activate_workout_plan_not_found(
        self,
        mock_ai_service,
        mock_workout_repo,
        mock_nutrition_repo,
        mock_user_repo
    ):
        """Test activation fails when plan doesn't exist"""
        # Arrange
        mock_workout_repo.get_by_id.return_value = None
        
        service = PlanningService(
            mock_ai_service,
            mock_workout_repo,
            mock_nutrition_repo,
            mock_user_repo
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Plan not found"):
            service.activate_workout_plan("plan_123", "user_123")
        
        mock_workout_repo.update.assert_not_called()
    
    def test_activate_workout_plan_unauthorized(
        self,
        mock_ai_service,
        mock_workout_repo,
        mock_nutrition_repo,
        mock_user_repo,
        sample_workout_plan
    ):
        """Test activation fails when user doesn't own the plan"""
        # Arrange
        mock_workout_repo.get_by_id.return_value = sample_workout_plan
        
        service = PlanningService(
            mock_ai_service,
            mock_workout_repo,
            mock_nutrition_repo,
            mock_user_repo
        )
        
        with pytest.raises(ValueError, match="Plan does not belong to this user"):
            service.activate_workout_plan("plan_123", "different_user")
        
        mock_workout_repo.update.assert_not_called()


class TestPlanningServiceNutritionGeneration:
    """Tests for nutrition plan generation"""
    
    def test_generate_nutrition_plan_success(
        self,
        mock_ai_service,
        mock_workout_repo,
        mock_nutrition_repo,
        mock_user_repo,
        sample_user
    ):
        """Test successful nutrition plan generation"""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user
        mock_ai_service.generate_nutrition_plan.return_value = {
            "daily_plans": [
                {
                    "day": "Monday",
                    "meals": [
                        {
                            "name": "Breakfast",
                            "description": "Oatmeal",
                            "calories": 400,
                            "protein": 15,
                            "carbs": 60,
                            "fats": 10,
                            "ingredients": ["oats", "banana"]
                        }
                    ]
                }
            ]
        }
        
        service = PlanningService(
            mock_ai_service,
            mock_workout_repo,
            mock_nutrition_repo,
            mock_user_repo
        )
        
        # Act
        result = service.generate_nutrition_plan("user_123")
        
        # Assert
        assert result is not None
        assert result.user_id == "user_123"
        assert len(result.daily_plans) == 1
        mock_nutrition_repo.save.assert_called_once()
        mock_ai_service.generate_nutrition_plan.assert_called_once()
