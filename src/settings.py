from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Server settings
    port: int = 5000
    
    # Processing settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()