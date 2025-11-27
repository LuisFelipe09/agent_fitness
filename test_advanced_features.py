import sys
import os
sys.path.append(os.getcwd())

from src.infrastructure.database import SessionLocal
from src.infrastructure.repositories import SqlAlchemyUserRepository
from src.domain.models import User
from src.application.role_service import RoleService
from src.infrastructure.repositories import SqlAlchemyPlanVersionRepository, SqlAlchemyNotificationRepository, SqlAlchemyPlanCommentRepository
import requests
import json
from datetime import datetime

# Setup DB access
db = SessionLocal()
user_repo = SqlAlchemyUserRepository(db)
role_service = RoleService(user_repo)

BASE_URL = "http://localhost:8000"
CLIENT_ID = "client_test_adv"
TRAINER_ID = "trainer_test_adv"

def setup_users():
    print("Setting up users...")
    # Create Client
    client = User(id=CLIENT_ID, username="Test Client", roles=["client"])
    
    # Add profile
    from src.domain.models import UserProfile, Goal, ActivityLevel
    client.profile = UserProfile(
        age=30,
        weight=80.0,
        height=180.0,
        gender="Male",
        goal=Goal.MUSCLE_GAIN,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        dietary_restrictions=[],
        injuries=[]
    )
    
    existing_client = user_repo.get_by_id(CLIENT_ID)
    if not existing_client:
        user_repo.save(client)
    else:
        # Update profile if exists
        existing_client.profile = client.profile
        user_repo.update(existing_client)
    
    # Create Trainer
    trainer = User(id=TRAINER_ID, username="Test Trainer", roles=["trainer"])
    existing_trainer = user_repo.get_by_id(TRAINER_ID)
    if not existing_trainer:
        user_repo.save(trainer)
    else:
        # Ensure role
        if "trainer" not in existing_trainer.roles:
            existing_trainer.roles.append("trainer")
            user_repo.update(existing_trainer)
            
    # Assign client to trainer
    # We can do this via RoleService or directly updating user
    client_user = user_repo.get_by_id(CLIENT_ID)
    client_user.trainer_id = TRAINER_ID
    user_repo.update(client_user)
    print("Users setup complete.")

def test_flow():
    setup_users()
    
    # 1. Client creates plan (Manual DB creation to bypass AI)
    print("\n1. Creating initial plan (Manual)...")
    from src.domain.models import WorkoutPlan, WorkoutSession, Exercise
    from src.infrastructure.repositories import SqlAlchemyWorkoutPlanRepository
    
    plan_repo = SqlAlchemyWorkoutPlanRepository(db)
    
    # Create dummy plan
    plan_id = f"plan_{int(datetime.now().timestamp())}"
    initial_plan = WorkoutPlan(
        id=plan_id,
        user_id=CLIENT_ID,
        start_date=datetime.now(),
        end_date=datetime.now(),
        sessions=[
            WorkoutSession(
                day="Monday",
                focus="Chest",
                exercises=[
                    Exercise(name="Bench Press", description="Press it", sets=3, reps="10", rest_time="60s")
                ]
            )
        ],
        created_by=CLIENT_ID,
        state="draft"
    )
    plan_repo.save(initial_plan)
    
    # Debug: Check if it exists in DB
    saved_plan = plan_repo.get_current_plan(CLIENT_ID)
    if saved_plan:
        print(f"DEBUG: Plan saved in DB: {saved_plan.id}")
    else:
        print("DEBUG: Plan NOT found in DB after save!")
    
    # Verify it exists via API
    # We don't have a get_plan endpoint for client yet? 
    # Actually we do: get_current_workout_plan
    res = requests.get(f"{BASE_URL}/users/{CLIENT_ID}/plans/workout/current", headers={"X-User-Id": CLIENT_ID})
    if res.status_code == 200:
        plan = res.json()
        print(f"✅ Plan created: {plan['id']} (State: {plan.get('state')})")
    else:
        print(f"❌ Failed to verify plan: {res.text}")
        return
    
    # 2. Trainer updates plan
    print("\n2. Trainer updating plan...")
    update_data = {
        "start_date": plan['start_date'],
        "end_date": plan['end_date'],
        "sessions": [
            {
                "day": "Monday",
                "focus": "Updated by Trainer",
                "exercises": [{"name": "Pushups", "description": "Harder", "sets": 4, "reps": "12", "rest_time": "60s"}]
            }
        ]
    }
    
    res = requests.put(
        f"{BASE_URL}/trainer/workout-plans/{plan_id}",
        headers={"X-User-Id": TRAINER_ID},
        json=update_data
    )
    
    if res.status_code != 200:
        print(f"❌ Failed to update plan: {res.text}")
        return
    
    updated_plan = res.json()['plan']
    print(f"✅ Plan updated. New State: {updated_plan.get('state')}")
    
    # 3. Check Versions
    print("\n3. Checking versions...")
    res = requests.get(f"{BASE_URL}/plans/{plan_id}/versions", headers={"X-User-Id": CLIENT_ID})
    versions = res.json()
    print(f"Found {len(versions)} versions")
    if len(versions) > 0:
        print(f"✅ Version 1 created by: {versions[0]['created_by']}")
    else:
        print("❌ No versions found!")
        
    # 4. Check Notifications
    print("\n4. Checking notifications...")
    res = requests.get(f"{BASE_URL}/notifications", headers={"X-User-Id": CLIENT_ID})
    notifs = res.json()
    print(f"Found {len(notifs)} notifications")
    if len(notifs) > 0:
        print(f"✅ Latest notification: {notifs[0]['title']} - {notifs[0]['message']}")
    else:
        print("❌ No notifications found!")
        
    # 5. Add Comment
    print("\n5. Adding comment...")
    res = requests.post(
        f"{BASE_URL}/plans/{plan_id}/comments",
        headers={"X-User-Id": CLIENT_ID},
        json={"content": "Looks great, thanks!", "is_internal": False}
    )
    if res.status_code == 200:
        print("✅ Comment added")
    else:
        print(f"❌ Failed to add comment: {res.text}")
        
    # 6. Get Comments
    print("\n6. Fetching comments...")
    res = requests.get(f"{BASE_URL}/plans/{plan_id}/comments", headers={"X-User-Id": TRAINER_ID})
    comments = res.json()
    print(f"Found {len(comments)} comments")
    if len(comments) > 0:
        print(f"✅ Comment content: {comments[0]['content']}")

    # 7. Activate Plan
    print("\n7. Activating plan...")
    # Plan should be 'approved' now
    res = requests.post(
        f"{BASE_URL}/users/{CLIENT_ID}/plans/workout/{plan_id}/activate",
        headers={"X-User-Id": CLIENT_ID}
    )
    
    if res.status_code == 200:
        active_plan = res.json()
        print(f"✅ Plan activated. New State: {active_plan.get('state')}")
        if active_plan.get('state') == 'active':
            print("✅ State verification passed")
        else:
            print("❌ State verification failed")
    else:
        print(f"❌ Failed to activate plan: {res.text}")

if __name__ == "__main__":
    test_flow()
