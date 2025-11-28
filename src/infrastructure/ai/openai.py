from src.infrastructure.ai.base import BaseAIService

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class OpenAIService(BaseAIService):
    """OpenAI implementation using Template Method Pattern"""
    
    def __init__(self, api_key: str):
        if OpenAI is None:
            raise ImportError("openai package is not installed. Please install it with `pip install openai`")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"  # Or gpt-3.5-turbo
    
    def _call_ai_api(self, prompt: str, system_message: str = "") -> str:
        """Call OpenAI API and return raw text response"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message or "You are a helpful assistant that outputs only JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise ValueError(f"Failed to generate plan from OpenAI: {e}")
