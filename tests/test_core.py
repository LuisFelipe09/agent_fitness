import pytest
from datetime import datetime
from src.domain.models import User, UserProfile, Goal, ActivityLevel
from src.application.user_service import UserService
from src.application.planning_service import PlanningService
from src.infrastructure.repositories import SqlAlchemyUserRepository, SqlAlchemyWorkoutPlanRepository, SqlAlchemyNutritionPlanRepository
from src.infrastructure.database import SessionLocal, Base, engine
from src.infrastructure.ai_service import GeminiAIService

# Setup test DB
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def user_service(db_session):
    return UserService(SqlAlchemyUserRepository(db_session))

@pytest.fixture
def planning_service(db_session):
    return PlanningService(
        GeminiAIService("dummy_key"),
        SqlAlchemyWorkoutPlanRepository(db_session),
        SqlAlchemyNutritionPlanRepository(db_session),
        SqlAlchemyUserRepository(db_session)
    )

def test_register_user(user_service):
    user = user_service.register_user("test_id_1", "test_user_1")
    assert user.id == "test_id_1"
    assert user.username == "test_user_1"

def test_update_profile(user_service):
    user_id = "test_id_1"
    profile = UserProfile(
        age=30,
        weight=80.0,
        height=180.0,
        gender="Male",
        goal=Goal.MUSCLE_GAIN,
        activity_level=ActivityLevel.MODERATELY_ACTIVE
    )
    updated_user = user_service.update_profile(user_id, profile)
    assert updated_user.profile.age == 30
    assert updated_user.profile.goal == Goal.MUSCLE_GAIN

def test_generate_workout_plan(planning_service, user_service):
    # Ensure user exists with profile
    user_id = "test_id_1"
    
    plan = planning_service.generate_workout_plan(user_id)
    assert plan is not None
    assert len(plan.sessions) > 0
    assert plan.sessions[0].day == "Monday"

def test_generate_nutrition_plan(planning_service):
    user_id = "test_id_1"
    plan = planning_service.generate_nutrition_plan(user_id)
    assert plan is not None
