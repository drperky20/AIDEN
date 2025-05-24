"""
Configuration module for Agno Gemini Agent Backend
"""
import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application settings and configuration"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False
    
    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]
    
    # Model Configuration - HARDCODED
    GOOGLE_API_KEY: str = "AIzaSyBHl9G6iCE9oGdoVuxWAU-SMzfHwGx6huM"
    GEMINI_MODEL_ID: str = "gemini-2.5-flash-preview-05-20"
    
    # Agent Configuration
    ENABLE_WEB_SEARCH: bool = True
    SHOW_TOOL_CALLS: bool = True
    ENABLE_MARKDOWN: bool = True
    
    # Environment - HARDCODED
    ENVIRONMENT: str = "development"
    
    def __init__(self):
        # Skip loading .env file since we're using hardcoded values
        pass
    
    def load_env_file(self) -> None:
        """Load environment variables from .env file if it exists - DISABLED"""
        # Disabled since we're using hardcoded values
        pass
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_api_key_valid(self) -> bool:
        """Check if Google API key is set and valid"""
        return bool(self.GOOGLE_API_KEY and self.GOOGLE_API_KEY != "your-google-api-key-here")

# Global settings instance
settings = Settings() 