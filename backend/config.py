"""
Configuration module for AIDEN V2 Backend
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file at the project root
# Assumes this config.py is in backend/, so .env is one level up.
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """Application settings and configuration"""

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "False").lower() in ("true", "1", "t")

    # CORS Configuration
    CORS_ORIGINS_STRING: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    CORS_ORIGINS: List[str] = [origin.strip() for origin in CORS_ORIGINS_STRING.split(',')]

    # Model Configuration - Default to OpenRouter with Llama 4 Maverick
    USE_OPENROUTER: bool = os.getenv("USE_OPENROUTER", "True").lower() in ("true", "1", "t")
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL_ID: str = os.getenv("OPENROUTER_MODEL_ID", "meta-llama/llama-4-maverick:free")
    
    # Fallback to Google Gemini if OpenRouter not available
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL_ID: str = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash-latest")

    # Voice Configuration
    ENABLE_VOICE_MODE: bool = os.getenv("ENABLE_VOICE_MODE", "True").lower() in ("true", "1", "t")
    ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel
    ELEVENLABS_MODEL_ID: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_flash_v2_5")  # Fastest model
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "tiny.en")  # Fastest for low latency
    VOICE_ACTIVATION_THRESHOLD: float = float(os.getenv("VOICE_ACTIVATION_THRESHOLD", "0.02"))
    MAX_SILENCE_DURATION: float = float(os.getenv("MAX_SILENCE_DURATION", "2.0"))

    # Agent Configuration
    ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "True").lower() in ("true", "1", "t")
    SHOW_TOOL_CALLS: bool = os.getenv("SHOW_TOOL_CALLS", "True").lower() in ("true", "1", "t")
    ENABLE_MARKDOWN: bool = os.getenv("ENABLE_MARKDOWN", "True").lower() in ("true", "1", "t")
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "5"))

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///../data/aiden_memory.db") # Path relative to backend dir for SQLite

    # Mem0 Configuration
    MEM0_API_KEY: Optional[str] = os.getenv("MEM0_API_KEY")

    # Project Root (useful for accessing files relative to the project root)
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_openrouter_valid(self) -> bool:
        """Check if OpenRouter configuration is valid"""
        return bool(self.OPENROUTER_API_KEY and len(self.OPENROUTER_API_KEY) > 20)

    @property
    def is_google_api_key_valid(self) -> bool:
        """Check if Google API key is set and seems valid"""
        return bool(self.GOOGLE_API_KEY and not self.GOOGLE_API_KEY.startswith("your") and len(self.GOOGLE_API_KEY) > 20)

    @property
    def is_elevenlabs_valid(self) -> bool:
        """Check if ElevenLabs configuration is valid"""
        return bool(self.ELEVENLABS_API_KEY and len(self.ELEVENLABS_API_KEY) > 20)

    @property
    def is_voice_mode_available(self) -> bool:
        """Check if voice mode can be enabled"""
        return self.ENABLE_VOICE_MODE and self.is_elevenlabs_valid

    @property
    def is_mem0_api_key_valid(self) -> bool:
        """Check if Mem0 API key is set"""
        return bool(self.MEM0_API_KEY)

    @property
    def preferred_model_type(self) -> str:
        """Get the preferred model type based on configuration"""
        if self.USE_OPENROUTER and self.is_openrouter_valid:
            return "openrouter"
        elif self.is_google_api_key_valid:
            return "gemini"
        else:
            return "none"

# Global settings instance
settings = Settings() 