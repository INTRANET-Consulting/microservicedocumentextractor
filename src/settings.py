from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal

class Settings(BaseSettings):
    # Server settings
    port: int = 5000
    
    # Processing settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Document processing strategy
    processing_strategy: Literal["auto", "fast", "hi_res", "ocr_only"] = "fast"
    
    # Table structure inference (only used with hi_res)
    infer_table_structure: bool = True
    
    # OCR languages (comma-separated, e.g., "eng,fra,deu")
    ocr_languages: str = "eng"
    
    # Enable chunking for large documents
    enable_chunking: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()