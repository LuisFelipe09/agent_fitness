"""
Shared pytest fixtures for all tests.
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from src.domain.models import (
    User, UserProfile, Goal, ActivityLevel,
    WorkoutPlan, WorkoutDay, Exercise,
    NutritionPlan, DailyMealPlan, Meal
)


# ============================================================================
# Mock Repository Fixtures
# ============================================================================

@pytest.fixture
def mock_user_repo():
    """Mock UserRepository for unit tests"""
    repo = Mock()
    repo.get_by_id = Mock(return_value=None)
    repo.save = Mock()
    repo.update = Mock()
    return repo


@pytest.fixture
def mock_workout_repo():
    """Mock WorkoutPlanRepository for unit tests"""
    repo = Mock()
    repo.get_by_id = Mock(return_value=None)
    repo.get_current_plan = Mock(return_value=None)
    repo.save = Mock()
    repo.update = Mock()
    return repo


@pytest.fixture
def mock_nutrition_repo():
    """Mock NutritionPlanRepository for unit tests"""
    repo = Mock()
    repo.get_by_id = Mock(return_value=None)
    repo.get_current_plan = Mock(return_value=None)
    repo.save = Mock()
    repo.update = Mock()
    return repo


@pytest.fixture
def mock_ai_service():
    """Mock AIService for unit tests"""
    service = Mock()
    service.generate_workout_plan = Mock()
    service.generate_nutrition_plan = Mock()
    return service


# ============================================================================
# Sample Domain Model Fixtures
# ============================================================================

@pytest.fixture
def sample_user():
    """Sample user with profile"""
    profile = UserProfile(
        age=30,
        weight=80.0,
        height=180.0,
        gender="Male",
        goal=Goal.MUSCLE_GAIN,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        dietary_restrictions=[],
        injuries=[]
    )
    
    return User(
        id="user_123",
        username="test_user",
        roles=["client"],
        profile=profile,
        created_at=datetime.now()
    )


@pytest.fixture
def sample_workout_plan():
    """Sample workout plan with new structure"""
    exercises = [
        Exercise(
            name="Bench Press",
            sets=3,
            reps="10",
            rest="60s",  # Changed from rest_time
            notes="Press the bar",
            description="Chest exercise"
        )
    ]
    
    workout_days = [
        WorkoutDay(
            day="Day 1",
            focus="Chest",
            exercises=exercises
        )
    ]
    
    return WorkoutPlan(
        id="plan_123",
        user_id="user_123",
        title="Test Workout Plan",
        description="A test plan for muscle building",
        weeks=4,
        days_per_week=3,
        workout_days=workout_days,
        created_at=datetime.now(),
        created_by="user_123",
        state="draft"
    )


@pytest.fixture
def sample_nutrition_plan():
    """Sample nutrition plan with new structure"""
    meals = [
        Meal(
            name="Breakfast",
            time="8:00 AM",
            foods=["oats", "banana", "berries"],
            calories=400,
            protein=15,
            carbs=60,
            fats=10,
            description="Oatmeal with fruits"
        )
    ]
    
    return NutritionPlan(
        id="nutrition_123",
        user_id="user_123",
        title="Test Nutrition Plan",
        description="A balanced nutrition plan",
        daily_calories=2000,
        protein_grams=150,
        carbs_grams=200,
        fats_grams=65,
        meals=meals,
        created_at=datetime.now(),
        created_by="user_123",
        state="draft"
    )

