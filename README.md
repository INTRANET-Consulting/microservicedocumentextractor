## Document Content Extractor Microservice

### Overview
A dedicated microservice for extracting text content from various document formats using the unstructured library. 

### CURL example
```bash
curl -X POST "http://localhost:8002/process" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/document.pdf"
```
