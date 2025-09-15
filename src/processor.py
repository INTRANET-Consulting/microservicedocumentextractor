import logging
import os
from typing import List, Tuple, Dict, Any
from fastapi import UploadFile
from unstructured.partition.auto import partition
import magic
import tempfile
from contextlib import contextmanager
import gc
from .models import ProcessedFile, DocumentElement
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
    async def extract_text(file: UploadFile, mime_type: str) -> Tuple[List[Dict], int]:
        """Extract structured elements from file using unstructured"""
        content = await file.read()
        
        try:
            file_ext = os.path.splitext(file.filename or "unknown.txt")[1]
            with temporary_file(suffix=file_ext) as temp_file:
                temp_file.write(content)
                temp_file.flush()
                
                # Use hi_res mode with table structure detection
                elements = partition(
                    filename=temp_file.name, 
                    strategy="hi_res",
                    infer_table_structure=True  # Preserves table formatting
                )
                
                # Convert to structured format
                structured_elements = []
                total_text_length = 0

                for element in elements:
                    element_text = str(element).strip()
                    if element_text:  # Only include non-empty elements
                        # Convert metadata to dictionary
                        metadata_dict = {}
                        if hasattr(element, 'metadata') and element.metadata:
                            # Convert ElementMetadata to dict
                            metadata_dict = element.metadata.to_dict() if hasattr(element.metadata, 'to_dict') else {}
                        
                        element_data = {
                            "type": element.__class__.__name__,
                            "text": element_text,
                            "metadata": metadata_dict
                        }
                        
                        # Add page number if available
                        if metadata_dict.get('page_number'):
                            element_data["page_number"] = metadata_dict.get('page_number')
                            
                        structured_elements.append(element_data)
                        total_text_length += len(element_text)

                logger.info(f"Extracted {len(structured_elements)} elements, total content length: {total_text_length}")
                return structured_elements, total_text_length
                
        finally:
            del content
            gc.collect()
            await file.seek(0)

    @staticmethod
    async def process_single_file(file: UploadFile) -> Tuple[List[Dict], ProcessedFile]:
        """Process a single file with proper resource cleanup"""
        logger.info(f"Processing file: {file.filename}")
        
        try:
            mime_type, _ = await DocumentProcessor.validate_file(file)
            structured_elements, text_length = await DocumentProcessor.extract_text(file, mime_type)
            
            processed_file = ProcessedFile(
                filename=file.filename or "unknown",
                file_type=mime_type,
                status="success",
                element_count=len(structured_elements),
                total_text_length=text_length
            )
            
            return structured_elements, processed_file
            
        except Exception as e:
            logger.error(f"Failed to process {file.filename}: {str(e)}")
            processed_file = ProcessedFile(
                filename=file.filename or "unknown",
                file_type=getattr(file, 'content_type', 'unknown'),
                status="error",
                error=str(e),
                element_count=0,
                total_text_length=0
            )
            return [], processed_file
        finally:
            gc.collect()

    @staticmethod 
    async def process_files(files: List[UploadFile]) -> Tuple[List[Dict], List[ProcessedFile], Dict[str, Any]]:
        """Process multiple files with memory management and return structured data"""
        logger.info(f"Processing {len(files)} files")
        
        all_elements = []
        processing_info = []
        
        try:
            for file in files:
                elements, info = await DocumentProcessor.process_single_file(file)
                if elements:
                    all_elements.extend(elements)
                processing_info.append(info)
            
            # Create summary
            element_types = {}
            total_text_length = 0
            for element in all_elements:
                element_type = element["type"]
                element_types[element_type] = element_types.get(element_type, 0) + 1
                total_text_length += len(element["text"])

            summary = {
                "total_elements": len(all_elements),
                "total_text_length": total_text_length,
                "element_types": element_types,
                "files_processed": len(files)
            }
            
            logger.info(f"Processed {len(files)} files, total elements: {len(all_elements)}")
            
            return all_elements, processing_info, summary
        finally:
            # Clean up after processing
            for file in files:
                await file.close()
            gc.collect()