from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DocumentElement(BaseModel):
    """Individual document element with metadata"""
    type: str  # e.g., "Title", "NarrativeText", "Table", "Header", etc.
    text: str
    metadata: Dict[str, Any] = {}
    page_number: Optional[int] = None
    
class ProcessedFile(BaseModel):
    """Information about processed file"""
    filename: str
    file_type: str
    status: str
    error: Optional[str] = None
    element_count: Optional[int] = None
    total_text_length: Optional[int] = None

class ProcessingResponse(BaseModel):
    """API response for document processing with structured elements"""
    elements: List[DocumentElement]
    processing_info: List[ProcessedFile]
    summary: Dict[str, Any] = {}