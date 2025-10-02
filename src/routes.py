from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import logging
from .processor import DocumentProcessor
from .models import ProcessingResponse, DocumentElement

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
    print("🟢 HEALTH CHECK CALLED - NEW CODE RUNNING!")
    logger.info("🟢 HEALTH CHECK CALLED - NEW CODE RUNNING!")
    return {
        "status": "healthy",
        "service": "document-content-extractor",
        "version": "0.1.0-DEBUG"
    }

@router.get("/debug-test")
async def debug_test():
    """Debug test to verify we're running the updated code"""
    print("🔍 DEBUG TEST CALLED - NEW CODE IS RUNNING!")
    logger.info("🔍 DEBUG TEST CALLED - NEW CODE IS RUNNING!")
    return {
        "message": "✅ NEW CODE IS RUNNING!",
        "timestamp": "2024-NEW-VERSION",
        "test": "success"
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
    # OBVIOUS DEBUG LOGGING - SHOULD BE VISIBLE IMMEDIATELY
    print("🚨🚨🚨 PROCESS_DOCUMENTS CALLED - NEW CODE RUNNING! 🚨🚨🚨")
    logger.info("🚨🚨🚨 PROCESS_DOCUMENTS CALLED - NEW CODE RUNNING! 🚨🚨🚨")
    print(f"🔍 Processing {len(files)} files: {[f.filename for f in files]}")
    logger.info(f"🔍 Processing {len(files)} files: {[f.filename for f in files]}")
    
    try:
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        print("🔄 About to call DocumentProcessor.process_files...")
        logger.info("🔄 About to call DocumentProcessor.process_files...")
        
        elements_data, processing_info, summary = await DocumentProcessor.process_files(files)
        
        print(f"🔍 DEBUG: Got {len(elements_data)} elements, {len(processing_info)} files")
        logger.info(f"🔍 DEBUG: Got {len(elements_data)} elements, {len(processing_info)} files")
        print(f"🔍 DEBUG: Summary keys: {list(summary.keys()) if isinstance(summary, dict) else 'not dict'}")
        logger.info(f"🔍 DEBUG: Summary keys: {list(summary.keys()) if isinstance(summary, dict) else 'not dict'}")
        
        # Convert Dict objects to DocumentElement objects
        print("🔄 Converting elements to DocumentElement objects...")
        logger.info("🔄 Converting elements to DocumentElement objects...")
        
        elements = [
            DocumentElement(
                type=elem["type"],
                text=elem["text"],
                metadata=elem.get("metadata", {}),
                page_number=elem.get("page_number")
            ) for elem in elements_data
        ]
        
        print(f"✅ Returning ProcessingResponse with {len(elements)} elements")
        logger.info(f"✅ Returning ProcessingResponse with {len(elements)} elements")
        
        return ProcessingResponse(
            elements=elements,
            processing_info=processing_info,
            summary=summary
        )
        
    except Exception as e:
        print(f"❌ ERROR in process_documents: {str(e)}")
        logger.error(f"❌ ERROR in process_documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents: {str(e)}"
        )
    finally:
        print("🧹 Cleaning up files...")
        logger.info("🧹 Cleaning up files...")
        # Cleanup
        for file in files:
            await file.close()