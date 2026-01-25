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
        Act as a professional fitness coach. Generate a personalized workout plan for a user with the following profile:
        - Age: {profile.age}
        - Gender: {profile.gender}
        - Weight: {profile.weight} kg
        - Height: {profile.height} cm
        - Goal: {profile.goal.value}
        - Activity Level: {profile.activity_level.value}
        - Injuries/Limitations: {', '.join(profile.injuries) if profile.injuries else 'None'}
        
        Return ONLY valid JSON (no markdown formatting) with the following structure:
        {{
            "title": "Catchy plan title based on goal",
            "description": "Brief description of the plan and what it will help achieve",
            "weeks": 4,
            "days_per_week": 4,
            "workout_days": [
                {{
                    "day": "Day 1",
                    "focus": "Push (Chest, Shoulders, Triceps)",
                    "exercises": [
                        {{
                            "name": "Bench Press",
                            "sets": 4,
                            "reps": "8-10",
                            "rest": "90s",
                            "notes": "Keep elbows at 45 degrees"
                        }}
                    ]
                }}
            ]
        }}
        
        Create {4 if profile.goal.value in ['muscle_gain', 'maintenance'] else 3} workout days.
        Keep exercises appropriate for the user's experience level based on their activity level.
        """
    
    def _build_nutrition_prompt(self, profile: UserProfile) -> str:
        """Build the nutrition plan generation prompt"""
        # Calculate approximate TDEE for calorie recommendations
        base_calories = 2000 if profile.gender == 'male' else 1700
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        multiplier = activity_multipliers.get(profile.activity_level.value, 1.55)
        estimated_tdee = int(base_calories * multiplier)
        
        # Adjust based on goal
        if profile.goal.value == 'weight_loss':
            target_calories = estimated_tdee - 500
        elif profile.goal.value == 'muscle_gain':
            target_calories = estimated_tdee + 300
        else:
            target_calories = estimated_tdee
            
        return f"""
        Act as a professional nutritionist. Generate a personalized nutrition plan for a user with the following profile:
        - Age: {profile.age}
        - Gender: {profile.gender}
        - Weight: {profile.weight} kg
        - Height: {profile.height} cm
        - Goal: {profile.goal.value}
        - Activity Level: {profile.activity_level.value}
        - Dietary Restrictions: {', '.join(profile.dietary_restrictions) if profile.dietary_restrictions else 'None'}
        - Estimated Daily Calorie Target: ~{target_calories} calories
        
        Return ONLY valid JSON (no markdown formatting) with the following structure:
        {{
            "title": "Catchy plan title based on goal and calories",
            "description": "Brief description of the nutrition approach and benefits",
            "daily_calories": {target_calories},
            "protein_grams": {int(target_calories * 0.3 / 4)},
            "carbs_grams": {int(target_calories * 0.4 / 4)},
            "fats_grams": {int(target_calories * 0.3 / 9)},
            "meals": [
                {{
                    "name": "Breakfast",
                    "time": "8:00 AM",
                    "foods": ["2 eggs scrambled", "1 slice whole grain toast", "1/2 avocado"],
                    "calories": 450,
                    "protein": 25,
                    "carbs": 30,
                    "fats": 28
                }},
                {{
                    "name": "Lunch",
                    "time": "12:30 PM",
                    "foods": ["Grilled chicken breast 150g", "Brown rice 1 cup", "Mixed vegetables"],
                    "calories": 550,
                    "protein": 45,
                    "carbs": 55,
                    "fats": 12
                }},
                {{
                    "name": "Snack",
                    "time": "4:00 PM",
                    "foods": ["Greek yogurt 200g", "Mixed nuts 30g"],
                    "calories": 300,
                    "protein": 20,
                    "carbs": 15,
                    "fats": 18
                }},
                {{
                    "name": "Dinner",
                    "time": "7:30 PM",
                    "foods": ["Salmon fillet 150g", "Quinoa 1 cup", "Steamed broccoli"],
                    "calories": 600,
                    "protein": 45,
                    "carbs": 45,
                    "fats": 25
                }}
            ]
        }}
        
        Adjust portions and meals to match the target macros.
        Respect any dietary restrictions mentioned.
        Make the plan practical and easy to follow.
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
