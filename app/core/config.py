from pydantic_settings import BaseSettings

"""
Application configuration management.

Loads environment variables using Pydantic settings.
"""

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    TESTING: bool = False

    class Config:
        env_file = ".env"

settings = Settings()