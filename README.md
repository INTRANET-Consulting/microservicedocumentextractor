


# Document Content Extractor

A high-performance FastAPI microservice for extracting structured content from various document formats using the Unstructured library. Enhanced version of Borut's microservice.

## Features

- **Multi-format Support**: Process PDF, DOCX, DOC, TXT, RTF, ODT, XLSX, XLS, PPTX, and PPT files
- **Intelligent Processing**: Multiple extraction strategies (fast, hi_res, auto, ocr_only)
- **Structured Output**: Returns typed elements (Title, NarrativeText, Table, Header, etc.) with metadata
- **Table Detection**: Advanced table structure inference with hi_res strategy
- **OCR Support**: Multi-language OCR capabilities
- **Memory Optimized**: Built-in garbage collection and resource cleanup
- **Batch Processing**: Handle multiple files in a single request

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd document-content-extractor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory (see Configuration section below)

5. Run the service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Configuration

Create a `.env` file with the following settings:

```properties
# Server Configuration
PORT=8002

# Processing Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Document Processing Strategy
# Options: "auto", "fast", "hi_res", "ocr_only"
# - fast: Quick text extraction, good for text-based PDFs
# - hi_res: Advanced ML processing with table detection, slower but more accurate
# - auto: Automatically choose based on document type
# - ocr_only: Force OCR processing
PROCESSING_STRATEGY=hi_res

# Table Structure Detection (only used with hi_res strategy)
INFER_TABLE_STRUCTURE=false

# OCR Languages (comma-separated language codes)
# Common codes: eng, fra, deu, spa, ita, por, rus, chi_sim, chi_tra, jpn, kor
OCR_LANGUAGES=eng,deu

# Enable document chunking for large files
ENABLE_CHUNKING=false
```

### Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `PORT` | 5000 | Server port |
| `MAX_FILE_SIZE` | 10485760 | Maximum file size in bytes (10MB) |
| `PROCESSING_STRATEGY` | fast | Extraction strategy: `auto`, `fast`, `hi_res`, `ocr_only` |
| `INFER_TABLE_STRUCTURE` | true | Enable table structure detection (hi_res only) |
| `OCR_LANGUAGES` | eng | Comma-separated language codes for OCR |
| `ENABLE_CHUNKING` | true | Enable chunking for large documents |

## API Endpoints

### Health Check
```http
GET /health
```

Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "document-content-extractor",
  "version": "0.1.0-DEBUG"
}
```

### Process Documents
```http
POST /process
Content-Type: multipart/form-data
```

Upload and process one or more documents.

**Parameters:**
- `files`: One or more files (multipart/form-data)

**Response:**
```json
{
  "elements": [
    {
      "type": "Title",
      "text": "Document Title",
      "metadata": {
        "page_number": 1,
        "filename": "document.pdf"
      },
      "page_number": 1
    },
    {
      "type": "NarrativeText",
      "text": "This is a paragraph of text...",
      "metadata": {...},
      "page_number": 1
    }
  ],
  "processing_info": [
    {
      "filename": "document.pdf",
      "file_type": "application/pdf",
      "status": "success",
      "element_count": 45,
      "total_text_length": 3421
    }
  ],
  "summary": {
    "total_elements": 45,
    "total_text_length": 3421,
    "element_types": {
      "Title": 3,
      "NarrativeText": 38,
      "Table": 2,
      "Header": 2
    },
    "files_processed": 1,
    "processing_strategy": "hi_res",
    "infer_table_structure": false
  }
}
```

## Usage Examples

### Python (requests)
```python
import requests

url = "http://localhost:8002/process"
files = [
    ('files', ('document.pdf', open('document.pdf', 'rb'), 'application/pdf')),
    ('files', ('report.docx', open('report.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
]

response = requests.post(url, files=files)
data = response.json()

for element in data['elements']:
    print(f"{element['type']}: {element['text'][:100]}...")
```

### cURL
```bash
curl -X POST "http://localhost:8002/process" \
  -F "files=@document.pdf" \
  -F "files=@report.docx"
```

### JavaScript (fetch)
```javascript
const formData = new FormData();
formData.append('files', fileInput.files[0]);

const response = await fetch('http://localhost:8002/process', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.elements);
```

## Element Types

The service returns various element types depending on document structure:

- **Title**: Document or section titles
- **NarrativeText**: Regular paragraphs and text
- **Table**: Tabular data (with structure when using hi_res)
- **Header**: Page or section headers
- **Footer**: Page footers
- **ListItem**: Bulleted or numbered list items
- **Image**: Image elements with metadata
- **Formula**: Mathematical formulas

## Processing Strategies

### Fast (Default)
- Quick text extraction
- Best for text-based PDFs and documents
- No table structure inference
- Lower memory usage

### Hi-Res
- Advanced ML-based processing
- Table structure detection
- Better accuracy for complex layouts
- Higher processing time and memory usage

### Auto
- Automatically selects strategy based on document type
- Balances speed and accuracy

### OCR Only
- Forces OCR processing
- Useful for scanned documents or images
- Supports multiple languages

## Performance Considerations

- **Memory**: The service includes automatic garbage collection and resource cleanup
- **File Size**: Default limit is 10MB per file (configurable)
- **Batch Processing**: Multiple files are processed sequentially
- **Strategy Impact**: `hi_res` is significantly slower but more accurate than `fast`

## Error Handling

The service returns detailed error information:

```json
{
  "processing_info": [
    {
      "filename": "corrupted.pdf",
      "file_type": "application/pdf",
      "status": "error",
      "error": "Failed to parse PDF: invalid format",
      "element_count": 0,
      "total_text_length": 0
    }
  ]
}
```

## Development

### Project Structure
```
document-content-extractor/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── routes.py        # API endpoints
│   ├── processor.py     # Document processing logic
│   ├── models.py        # Pydantic models
│   └── settings.py      # Configuration management
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
└── README.md
```

### Running Tests
```bash
pytest tests/
```

### Debug Mode
The service includes debug endpoints:
```http
GET /debug-test
```

## Dependencies

- **FastAPI**: Web framework
- **Unstructured**: Document parsing library
- **Pydantic**: Data validation
- **Python-multipart**: File upload handling