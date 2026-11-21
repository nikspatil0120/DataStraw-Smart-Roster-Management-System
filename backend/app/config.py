"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Database - explicitly read from env
    database_url: str = Field(default="postgresql://postgres:postgres@localhost:5432/datastraw")
    sqlalchemy_echo: bool = False
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Scheduling
    solver_time_limit_seconds: int = 60
    solver_random_seed: int = 42
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Allow reading DATABASE_URL environment variable
        fields = {
            "database_url": {
                "env": ["database_url", "DATABASE_URL"]
            }
        }


settings = Settings()
# Debug: print what was loaded
print(f"[CONFIG] Loaded database_url: {settings.database_url[:50]}...")
