import os
from typing import Optional
from functools import lru_cache
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

@dataclass
class Settings:
    # App
    APP_NAME: str = "AI Fitness Agent"
    DEBUG: bool = True
    
    # Database - use 'or' to handle empty string from .env
    DATABASE_URL: str = os.getenv("DATABASE_URL") or "sqlite:///./fitness_agent.db"
    
    # AI Providers
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or None
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY") or None
    
    # AI Configuration
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER") or "gemini"

@lru_cache()
def get_settings():
    return Settings()
