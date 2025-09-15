from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import logging
from .processor import DocumentProcessor
from .models import ProcessingResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Check service health status
    
    Returns:
        dict: Service health information
    """
    return {
        "status": "healthy",
        "service": "document-content-extractor",
        "version": "0.1.0"
    }

@router.post("/process", response_model=ProcessingResponse)
async def process_documents(
    files: List[UploadFile] = File(...),
) -> ProcessingResponse:
    """
    Process documents and extract their content.
    
    Args:
        files: List of files to process
        
    Returns:
        ProcessingResponse with extracted content and processing info
    """
    try:
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        content, processing_info = await DocumentProcessor.process_files(files)
        
        return ProcessingResponse(
            content=content,
            processing_info=processing_info
        )
        
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents: {str(e)}"
        )
    finally:
        # Cleanup
        for file in files:
            await file.close()