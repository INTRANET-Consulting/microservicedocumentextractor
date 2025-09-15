import logging
import os
from typing import List, Tuple
from fastapi import UploadFile
from unstructured.partition.auto import partition
import magic
import tempfile
from contextlib import contextmanager
import gc
from .models import ProcessedFile
from .settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def temporary_file(suffix: str = None):
    """Context manager for handling temporary files with proper cleanup"""
    temp_file = None
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        yield temp_file
    finally:
        if temp_file:
            temp_file.close()
            try:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")

class DocumentProcessor:
    """Handles document processing with memory management"""
    
    @staticmethod
    async def validate_file(file: UploadFile) -> Tuple[str, int]:
        """Validate file size and type"""
        settings = get_settings()
        content = None
        try:
            content = await file.read()
            file_size = len(content)
            
            if file_size > settings.max_file_size:
                raise ValueError(f"File size exceeds limit of {settings.max_file_size} bytes")

            mime_type = magic.Magic(mime=True).from_buffer(content)
            logger.info(f"Detected MIME type: {mime_type}")
            
            return mime_type, file_size
        finally:
            if content:
                del content
                gc.collect()
            await file.seek(0)

    @staticmethod
    async def extract_text(file: UploadFile, mime_type: str) -> str:
        """Extract text content from file using unstructured"""
        content = await file.read()
        
        try:
            with temporary_file(suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_file.write(content)
                temp_file.flush()
                
                elements = partition(filename=temp_file.name)
                text_content = "\n".join([str(element) for element in elements])
                
                logger.info(f"Extracted {len(text_content)} characters from {file.filename}")
                return text_content
                
        finally:
            del content
            gc.collect()
            await file.seek(0)

    @staticmethod
    async def process_single_file(file: UploadFile) -> Tuple[str, ProcessedFile]:
        """Process a single file with proper resource cleanup"""
        logger.info(f"Processing file: {file.filename}")
        
        try:
            mime_type, _ = await DocumentProcessor.validate_file(file)
            text_content = await DocumentProcessor.extract_text(file, mime_type)
            
            processed_file = ProcessedFile(
                filename=file.filename,
                file_type=mime_type,
                status="success"
            )
            
            return text_content, processed_file
            
        except Exception as e:
            logger.error(f"Failed to process {file.filename}: {str(e)}")
            processed_file = ProcessedFile(
                filename=file.filename,
                file_type=getattr(file, 'content_type', 'unknown'),
                status="error",
                error=str(e)
            )
            return "", processed_file
        finally:
            gc.collect()

    @staticmethod 
    async def process_files(files: List[UploadFile]) -> Tuple[str, List[ProcessedFile]]:
        """Process multiple files with memory management"""
        logger.info(f"Processing {len(files)} files")
        
        processed_contents = []
        processing_info = []
        
        try:
            for file in files:
                content, info = await DocumentProcessor.process_single_file(file)
                if content:
                    processed_contents.append(content)
                processing_info.append(info)
            
            combined_content = "\n\n".join(processed_contents)
            logger.info(f"Processed {len(files)} files, total content length: {len(combined_content)}")
            
            return combined_content, processing_info
        finally:
            # Clean up after processing
            for file in files:
                await file.close()
            gc.collect()