# Technical Components & Dependencies

This document provides detailed information about all libraries, tools, and components used in the Document Content Extractor microservice.

## Core Framework

### FastAPI
- **Version**: Latest stable
- **Purpose**: Web framework for building the REST API
- **Features Used**:
  - Async request handling
  - Automatic API documentation (Swagger/OpenAPI)
  - Pydantic integration for data validation
  - File upload handling with multipart/form-data
  - CORS middleware
  - Lifecycle management (startup/shutdown events)

### Uvicorn
- **Purpose**: ASGI server for running FastAPI applications
- **Features**: High-performance async server with HTTP/1.1 and WebSocket support

## Document Processing

### Unstructured
- **Library**: `unstructured`
- **Purpose**: Core document parsing and content extraction library
- **Capabilities**:
  - Multi-format document parsing (PDF, DOCX, XLSX, PPTX, etc.)
  - Element type detection (Title, NarrativeText, Table, Header, Footer, etc.)
  - Metadata extraction (page numbers, coordinates, file information)
  - Multiple processing strategies (fast, hi_res, auto, ocr_only)
  - Table structure inference with machine learning models

#### Processing Strategies Breakdown

**Fast Strategy**:
- Direct text extraction without ML models
- Rule-based element detection
- Minimal dependencies
- Best for: Text-heavy PDFs, DOCX files with clear structure

**Hi-Res Strategy**:
- Uses computer vision and ML models
- Layout analysis with Detectron2 (Facebook AI)
- Table structure detection with ML
- Element classification with advanced heuristics
- Best for: Complex layouts, forms, scientific papers, scanned documents

**Auto Strategy**:
- Intelligent strategy selection based on document type
- Analyzes document characteristics first
- Falls back to appropriate strategy

**OCR-Only Strategy**:
- Forces OCR processing for all content
- Bypasses native text extraction
- Best for: Scanned documents, images, poor-quality PDFs

### OCR (Optical Character Recognition)

#### Tesseract OCR
- **Backend**: Tesseract 4.x (via pytesseract)
- **Purpose**: Text recognition from images and scanned documents
- **Language Support**: 100+ languages
- **Used When**: 
  - Processing scanned documents
  - OCR-only strategy selected
  - Hi-res strategy encounters image-based text

#### Supported OCR Languages
The service supports multi-language OCR through Tesseract's language packs:
- **English** (eng)
- **German** (deu)
- **French** (fra)
- **Spanish** (spa)
- **Italian** (ita)
- **Portuguese** (por)
- **Russian** (rus)
- **Chinese Simplified** (chi_sim)
- **Chinese Traditional** (chi_tra)
- **Japanese** (jpn)
- **Korean** (kor)
- Many more available through Tesseract

## Computer Vision & ML

### Detectron2 (Optional - Hi-Res Mode)
- **Developer**: Facebook AI Research (FAIR)
- **Purpose**: Object detection and layout analysis
- **Used For**:
  - Page layout detection
  - Table boundary detection
  - Image and figure identification
  - Complex document structure analysis
- **Note**: Only loaded when using hi_res strategy

### PDF Processing Libraries

#### PDFMiner / pdfplumber
- **Purpose**: PDF text extraction and analysis
- **Features**:
  - Text extraction with position information
  - Table detection
  - Metadata extraction
  - Font and formatting information

#### PyPDF2 / pypdf
- **Purpose**: PDF manipulation and reading
- **Features**:
  - Page extraction
  - Metadata reading
  - PDF structure analysis

## Office Document Processing

### python-docx
- **Purpose**: Microsoft Word (.docx) file processing
- **Capabilities**:
  - Paragraph and heading extraction
  - Table parsing
  - Style and formatting information
  - Metadata extraction

### python-pptx
- **Purpose**: PowerPoint (.pptx) presentation processing
- **Capabilities**:
  - Slide content extraction
  - Text box and shape parsing
  - Table extraction
  - Notes and comments

### openpyxl
- **Purpose**: Excel (.xlsx) spreadsheet processing
- **Capabilities**:
  - Cell value extraction
  - Sheet parsing
  - Formula handling
  - Formatting information

### olefile
- **Purpose**: Legacy Office format support (.doc, .xls, .ppt)
- **Capabilities**:
  - OLE (Object Linking and Embedding) file parsing
  - Binary Office format support

## Image Processing

### Pillow (PIL)
- **Purpose**: Image manipulation and processing
- **Used For**:
  - Image format conversion
  - Image preprocessing for OCR
  - Thumbnail generation
  - Image metadata extraction

### OpenCV (cv2) - Optional
- **Purpose**: Advanced image processing
- **Used For**:
  - Image enhancement before OCR
  - Noise reduction
  - Skew correction
  - Binarization

## Data Validation & Serialization

### Pydantic
- **Version**: 2.x
- **Purpose**: Data validation and settings management
- **Features Used**:
  - Request/response model validation
  - Environment variable parsing (pydantic-settings)
  - Automatic JSON serialization
  - Type checking and conversion

### pydantic-settings
- **Purpose**: Configuration management from environment variables
- **Features**: Type-safe settings with automatic `.env` file loading

## Utility Libraries

### python-multipart
- **Purpose**: Handle multipart/form-data requests
- **Used For**: File upload processing in FastAPI

### aiofiles
- **Purpose**: Async file I/O operations
- **Used For**: Non-blocking file reading/writing

### python-magic / mimetypes
- **Purpose**: File type detection
- **Used For**: Identifying uploaded file types and MIME type detection

## System Architecture

### Memory Management

#### Garbage Collection
- **Library**: Python's built-in `gc` module
- **Implementation**: 
  - Explicit collection after processing each file
  - Cleanup in finally blocks
  - Resource tracking and cleanup

#### Temporary File Management
- **Library**: `tempfile` module
- **Implementation**:
  - Context managers for automatic cleanup
  - Secure temporary file creation
  - Automatic deletion after processing

### Context Managers
- **Purpose**: Resource lifecycle management
- **Implementation**:
  - Custom context managers for temp files
  - AsyncContextManager for app lifecycle
  - Automatic cleanup in error scenarios

## Optional Machine Learning Models

When using **hi_res** strategy, the following models may be downloaded and cached:

### Layout Detection Models
- **Detectron2 Layout Model**: Document layout analysis
- **Table Transformer**: Table structure recognition
- **Element Classification Models**: Trained on various document types

### Model Storage
- Models are cached in: `~/.cache/huggingface/` or custom cache directory
- First run downloads models (can be several hundred MB)
- Subsequent runs use cached models

## Performance Dependencies

### Processing Time Factors
1. **Document Size**: Larger files take longer
2. **Strategy Selection**: 
   - Fast: ~1-2 seconds per document
   - Hi-Res: ~10-30 seconds per document
   - OCR-Only: ~5-15 seconds per page
3. **Image Content**: More images = longer processing
4. **Table Complexity**: Complex tables increase processing time

### Resource Requirements

**Minimum (Fast Strategy)**:
- RAM: 512 MB
- CPU: 1 core
- Storage: 500 MB (for libraries)

**Recommended (Hi-Res Strategy)**:
- RAM: 4-8 GB
- CPU: 4+ cores
- Storage: 5 GB (for ML models)
- GPU: Optional but significantly improves hi_res performance

## Network Dependencies

### Model Downloads (First Run)
- Hugging Face model hub: For downloading ML models
- Tesseract language data: For OCR language packs

### No External API Calls
- All processing is done locally
- No data sent to external services
- Complete data privacy and security

## Installation Requirements

### System Dependencies

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-deu \
    libtesseract-dev \
    poppler-utils \
    libmagic1
```

**macOS**:
```bash
brew install tesseract
brew install tesseract-lang
brew install poppler
brew install libmagic
```

**Windows**:
- Tesseract: Download installer from GitHub
- Poppler: Download binary from poppler Windows builds
- Set PATH environment variables appropriately

### Python Package Dependencies

**Core Packages** (from requirements.txt):
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
unstructured[all-docs]>=0.10.0
python-multipart>=0.0.6
pydantic>=2.4.0
pydantic-settings>=2.0.0
python-magic>=0.4.27
pytesseract>=0.3.10
Pillow>=10.0.0
```

**Unstructured Dependencies** (installed with [all-docs]):
```txt
pdf2image
pdfminer.six
pypdf
python-docx
python-pptx
openpyxl
python-magic
pillow
```

## Environment Variables Impact

| Variable | Components Affected |
|----------|-------------------|
| `PROCESSING_STRATEGY` | Determines which models/libraries are loaded |
| `INFER_TABLE_STRUCTURE` | Enables/disables Table Transformer model |
| `OCR_LANGUAGES` | Determines which Tesseract language packs to use |
| `MAX_FILE_SIZE` | Memory allocation and buffer sizes |

## Version Compatibility

- **Python**: 3.8, 3.9, 3.10, 3.11 (tested)
- **OS**: Linux, macOS, Windows
- **Architecture**: x86_64, ARM64 (Apple Silicon compatible)

## Security Considerations

### File Processing
- All files processed in isolated temporary directories
- Automatic cleanup prevents file system pollution
- No files stored permanently without explicit configuration

### Data Privacy
- No external API calls
- All processing local
- No telemetry or tracking
- Memory cleared after processing

## Troubleshooting Common Issues

### Missing System Dependencies
**Issue**: ImportError or library not found  
**Solution**: Install system dependencies (Tesseract, Poppler, libmagic)

### Out of Memory (OOM)
**Issue**: Process killed during hi_res processing  
**Solution**: Reduce MAX_FILE_SIZE or switch to fast strategy

### Slow Processing
**Issue**: Documents take too long to process  
**Solution**: Use fast strategy for simple documents, reserve hi_res for complex layouts

### OCR Language Not Found
**Issue**: Tesseract language pack missing  
**Solution**: Install required language pack: `sudo apt-get install tesseract-ocr-<lang>`