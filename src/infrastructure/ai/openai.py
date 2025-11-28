import os
import json
from typing import Dict, Any
from src.application.interfaces import AIService
from src.domain.models import UserProfile

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class OpenAIService(AIService):
    def __init__(self, api_key: str):
        if OpenAI is None:
            raise ImportError("openai package is not installed. Please install it with `pip install openai`")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview" # Or gpt-3.5-turbo

    def generate_workout_plan(self, profile: UserProfile) -> Dict[str, Any]:
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
                            "rest_time": "60s",
                            "video_url": "optional_url"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful fitness assistant that outputs only JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            return data
        except Exception as e:
            print(f"Error generating workout plan with OpenAI: {e}")
            raise ValueError("Failed to generate workout plan from OpenAI")

    def generate_nutrition_plan(self, profile: UserProfile) -> Dict[str, Any]:
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful nutritionist assistant that outputs only JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            return data
        except Exception as e:
            print(f"Error generating nutrition plan with OpenAI: {e}")
            raise ValueError("Failed to generate nutrition plan from OpenAI")
