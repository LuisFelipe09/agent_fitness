import os
from typing import Optional
from functools import lru_cache
from dataclasses import dataclass

@dataclass
class Settings:
    # App
    APP_NAME: str = "AI Fitness Agent"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fitness_agent.db")
    
    # AI Providers
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # AI Configuration
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "gemini") # gemini or openai

@lru_cache()
def get_settings():
    return Settings()
