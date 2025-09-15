# Local Development Setup Guide

This guide will help you set up the Document Content Extractor service on your local Windows machine using VS Code and Anaconda.

## Prerequisites

- Windows 10/11
- VS Code installed
- Anaconda or Miniconda installed
- Git installed

## Option 1: Using Anaconda (Recommended)

Anaconda is **highly recommended** for this project because:
- It handles complex dependencies better than pip alone
- Provides better isolation for machine learning packages
- Manages system-level dependencies more reliably
- Better compatibility with packages like unstructured, torch, etc.

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd document-content-extractor
```

### Step 2: Create Anaconda Environment

```bash
# Create a new conda environment with Python 3.11
conda create -n doc-extractor python=3.11 -y

# Activate the environment
conda activate doc-extractor
```

### Step 3: Install System Dependencies

```bash
# Install conda-forge packages first (better compatibility)
conda install -c conda-forge python-magic -y
conda install -c conda-forge libmagic -y
```

### Step 4: Install Python Dependencies

```bash
# Install core dependencies
pip install fastapi uvicorn python-multipart pdfplumber python-dotenv pydantic pydantic-settings

# Install unstructured with basic features
pip install unstructured

# Optional: Install additional unstructured features (large download)
# pip install "unstructured[all-docs]"
```

### Step 5: Windows-Specific Setup

For Windows, you may need additional setup for python-magic:

```bash
# If you encounter python-magic issues, install python-magic-bin instead
pip uninstall python-magic
pip install python-magic-bin==0.4.14
```

### Step 6: VS Code Setup

1. Open the project in VS Code
2. Install Python extension for VS Code
3. Select the conda environment:
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the `doc-extractor` environment

### Step 7: Run the Application

```bash
# Make sure you're in the project directory and environment is activated
conda activate doc-extractor

# Run the development server
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

## Option 2: Using Regular Python Virtual Environment

If you prefer not to use Anaconda:

### Step 1: Create Virtual Environment

```bash
# Create virtual environment
python -m venv doc-extractor-env

# Activate on Windows
doc-extractor-env\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements-without-locks.txt
```

Create a `requirements-without-locks.txt` file with core dependencies:

```
fastapi>=0.104.1
uvicorn>=0.24.0
python-multipart>=0.0.6
pdfplumber>=0.10.3
python-magic>=0.4.27
python-dotenv>=1.0.0
pydantic>=2.5.2
pydantic-settings>=2.1.0
unstructured
```

### Step 3: Handle Windows Magic Library

```bash
# Install Windows-compatible magic library
pip uninstall python-magic
pip install python-magic-bin==0.4.14
```

## Environment Configuration

Create a `.env` file in the project root:

```env
# Server settings
PORT=8002

# Processing settings
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

## Running the Application

### Development Mode

```bash
# With auto-reload for development
uvicorn src.main:app --host localhost --port 8002 --reload
```

### Production Mode

```bash
# Without auto-reload
uvicorn src.main:app --host 0.0.0.0 --port 8002
```

## Testing the API

Once running, you can test the API:

### Health Check

```bash
curl http://localhost:8002/health
```

### Process Documents

```bash
curl -X POST "http://localhost:8002/process" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@path/to/your/document.pdf"
```

## Troubleshooting

### Common Windows Issues

1. **Python-magic errors**: Use `python-magic-bin` instead of `python-magic`
2. **Permission errors**: Run terminal as administrator if needed
3. **Path issues**: Make sure Python and pip are in your PATH

### Large Dependencies

If you experience issues with large packages:

1. **Use conda for heavy packages**: `conda install numpy scipy torch -c pytorch`
2. **Increase pip timeout**: `pip install --timeout 300 unstructured`
3. **Install without optional dependencies**: `pip install unstructured --no-deps` then install deps separately

### VS Code Configuration

Add to your `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./doc-extractor-env/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true
}
```

## Recommended: Anaconda vs Regular Virtual Environment

**Use Anaconda if**:
- You plan to work with machine learning packages
- You want better dependency management
- You're dealing with packages that have complex system dependencies
- You want easier package conflict resolution

**Use regular venv if**:
- You prefer lightweight environments
- You have simpler dependency requirements
- You're familiar with pip and prefer that workflow

## Development Workflow

1. Always activate your environment first:
   ```bash
   conda activate doc-extractor  # or activate your venv
   ```

2. Install new packages:
   ```bash
   pip install package-name
   # Then update your requirements file
   pip freeze > requirements.txt
   ```

3. Run tests (if available):
   ```bash
   pytest tests/
   ```

## Performance Notes

- The first time you process documents, it may be slow as models download
- Consider using SSD storage for better performance
- Large documents require more RAM - monitor memory usage

## Security Notes

- Never commit API keys or secrets to version control
- Use environment variables for configuration
- Consider running behind a reverse proxy in production