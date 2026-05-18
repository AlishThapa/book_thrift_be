from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    app_name: str = Field(default="BookThrift API", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database Settings
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # JWT Settings
    secret_key: str = Field(default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS Settings
    allowed_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()