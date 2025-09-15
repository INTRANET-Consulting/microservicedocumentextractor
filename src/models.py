from pydantic import BaseModel
from typing import Optional, List

class ProcessedFile(BaseModel):
    """Information about processed file"""
    filename: str
    file_type: str
    status: str
    error: Optional[str] = None

class ProcessingResponse(BaseModel):
    """API response for document processing"""
    content: str
    processing_info: List[ProcessedFile]