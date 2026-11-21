"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Database - automatically reads DATABASE_URL from environment
    database_url: str = "postgresql://postgres:postgres@localhost:5432/datastraw"
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
    
    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
# Debug: print what was loaded
db_url = settings.database_url
print(f"[CONFIG] Loaded database_url: {db_url[:60] if db_url else 'EMPTY'}...")
print(f"[CONFIG] DATABASE_URL from env: {os.getenv('DATABASE_URL', 'NOT SET')[:60] if os.getenv('DATABASE_URL') else 'NOT SET'}...")
