from abc import ABC, abstractmethod
import json
from typing import Dict, Any
from src.application.interfaces import AIService
from src.domain.models import UserProfile


class BaseAIService(AIService, ABC):
    """Base class for AI services using Template Method Pattern"""
    
    def generate_workout_plan(self, profile: UserProfile) -> Dict[str, Any]:
        prompt = self._build_workout_prompt(profile)
        response_text = self._call_ai_api(prompt, system_message="You are a helpful fitness assistant that outputs only JSON.")
        return self._parse_json_response(response_text)
    
    def generate_nutrition_plan(self, profile: UserProfile) -> Dict[str, Any]:
        prompt = self._build_nutrition_prompt(profile)
        response_text = self._call_ai_api(prompt, system_message="You are a helpful nutritionist assistant that outputs only JSON.")
        return self._parse_json_response(response_text)
    
    def _build_workout_prompt(self, profile: UserProfile) -> str:
        """Build the workout plan generation prompt"""
        return f"""
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
    
    def _build_nutrition_prompt(self, profile: UserProfile) -> str:
        """Build the nutrition plan generation prompt"""
        return f"""
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
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response, handling markdown code blocks"""
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_text)
    
    @abstractmethod
    def _call_ai_api(self, prompt: str, system_message: str = "") -> str:
        """
        Call the specific AI provider's API.
        Must be implemented by subclasses.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message for the AI
            
        Returns:
            The raw text response from the API
        """
        pass
