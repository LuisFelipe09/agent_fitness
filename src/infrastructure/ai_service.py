import google.generativeai as genai
import os
import json
import uuid
from datetime import datetime, timedelta
from src.application.interfaces import AIService
from src.domain.models import UserProfile, WorkoutPlan, NutritionPlan, WorkoutSession, DailyMealPlan, Exercise, Meal

class GeminiAIService(AIService):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_workout_plan(self, profile: UserProfile) -> WorkoutPlan:
        prompt = f"""
        Act as a professional fitness coach. Generate a 1-week workout plan for a user with the following profile:
        - Age: {profile.age}
        - Gender: {profile.gender}
        - Goal: {profile.goal.value}
        - Activity Level: {profile.activity_level.value}
        - Injuries: {', '.join(profile.injuries) if profile.injuries else 'None'}
        
        Return ONLY valid JSON (no markdown formatting) with the following structure:
        {{
            "sessions": [
                {{
                    "day": "Monday",
                    "focus": "Upper Body",
                    "exercises": [
                        {{
                            "name": "Exercise Name",
                            "description": "Brief description",
                            "sets": 3,
                            "reps": "10-12",
                            "rest_time": "60s"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean response if it contains markdown code blocks
            text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(text)
            
            sessions = []
            for s in data['sessions']:
                exercises = [Exercise(**e) for e in s['exercises']]
                sessions.append(WorkoutSession(day=s['day'], focus=s['focus'], exercises=exercises))

            return WorkoutPlan(
                id=str(uuid.uuid4()),
                user_id="temp", # Will be set by service
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=7),
                sessions=sessions
            )
        except Exception as e:
            print(f"Error generating workout plan: {e}")
            # Fallback to a basic plan or re-raise
            raise ValueError("Failed to generate workout plan from AI")

    def generate_nutrition_plan(self, profile: UserProfile) -> NutritionPlan:
        prompt = f"""
        Act as a professional nutritionist. Generate a 1-week meal plan for a user with the following profile:
        - Age: {profile.age}
        - Gender: {profile.gender}
        - Goal: {profile.goal.value}
        - Activity Level: {profile.activity_level.value}
        - Dietary Restrictions: {', '.join(profile.dietary_restrictions) if profile.dietary_restrictions else 'None'}
        
        Return ONLY valid JSON (no markdown formatting) with the following structure:
        {{
            "daily_plans": [
                {{
                    "day": "Monday",
                    "meals": [
                        {{
                            "name": "Breakfast",
                            "description": "Oatmeal with fruits",
                            "calories": 400,
                            "protein": 15,
                            "carbs": 60,
                            "fats": 10,
                            "ingredients": ["oats", "milk", "banana"]
                        }}
                    ]
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(text)
            
            daily_plans = []
            for d in data['daily_plans']:
                meals = [Meal(**m) for m in d['meals']]
                daily_plans.append(DailyMealPlan(day=d['day'], meals=meals))

            return NutritionPlan(
                id=str(uuid.uuid4()),
                user_id="temp",
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=7),
                daily_plans=daily_plans
            )
        except Exception as e:
            print(f"Error generating nutrition plan: {e}")
            raise ValueError("Failed to generate nutrition plan from AI")
