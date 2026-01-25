from google import genai
from google.genai import types
from src.infrastructure.ai.base import BaseAIService


class GeminiAIService(BaseAIService):
    """Gemini AI implementation using Template Method Pattern"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.0-flash-exp'
    
    def _call_ai_api(self, prompt: str, system_message: str = "") -> str:
        """Call Gemini API and return raw text response"""
        try:
            config = None
            if system_message:
                config = types.GenerateContentConfig(
                    system_instruction=system_message
                )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise ValueError(f"Failed to generate plan from Gemini AI: {e}")
