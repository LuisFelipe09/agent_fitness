import google.generativeai as genai
from src.infrastructure.ai.base import BaseAIService


class GeminiAIService(BaseAIService):
    """Gemini AI implementation using Template Method Pattern"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def _call_ai_api(self, prompt: str, system_message: str = "") -> str:
        """Call Gemini API and return raw text response"""
        try:
            # Gemini doesn't have a separate system message, so we can ignore it
            # or prepend it to the prompt if needed
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise ValueError(f"Failed to generate plan from Gemini AI: {e}")
