# Environment Setup Guide

## Prerequisites
- Python 3.10+ installed
- `pip` and `venv` available

## Setup

1. **Clone and navigate to project**
   ```bash
   cd fitness-journey-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate virtual environment**
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

4. **Upgrade pip**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

5. **Install production dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   OR for development (includes testing/linting tools):
   ```bash
   pip install -r requirements-dev.txt
   ```

6. **Verify installation**
   ```bash
   python -c "import fastapi, torch, transformers; print('✓ All imports OK')"
   ```

7. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (see section below)
   ```

---

## Environment Variables Setup

### Step 1: Create .env file
```bash
cp .env.example .env
```

### Step 2: Edit .env with your settings

Open `.env` and configure the following:

**For Local Development** (minimal config):
```bash
API_PORT=8000
DEBUG=True
# Use SQLite for quick setup: DATABASE_URL=sqlite:///./fitness.db
DATABASE_URL=postgresql://postgres:password@localhost:5432/fitness_analyzer
JWT_SECRET_KEY=dev-key-123-change-me
```

**For Production** (secure config):
```bash
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
DATABASE_URL=postgresql://user:secure_password@prod-host:5432/fitness_analyzer
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### Step 3: Verify configuration loads
```bash
python -c "from backend.app.core.config import settings; print(f'✓ API will run on {settings.api_host}:{settings.api_port}')"
```

---

## Configuration Details

### API Configuration
- **API_HOST**: Server bind address (0.0.0.0 for external access)
- **API_PORT**: Port number (default 8000)
- **API_WORKERS**: Number of worker processes (default 4)
- **DEBUG**: Enable debug mode (True for dev, False for production)

### Database Configuration
- **DATABASE_URL**: Connection string
  - PostgreSQL: `postgresql://user:password@localhost:5432/dbname`
  - SQLite (dev only): `sqlite:///./fitness.db`
- **DATABASE_POOL_SIZE**: Connection pool size (default 20)
- **DATABASE_MAX_OVERFLOW**: Max overflow connections (default 10)

### Authentication & Security
- **JWT_SECRET_KEY**: Secret key for signing tokens (change in production!)
  Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **JWT_ALGORITHM**: Algorithm for signing (default HS256)
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Token expiration time (default 30)
- **REFRESH_TOKEN_EXPIRE_DAYS**: Refresh token lifetime (default 7)

### File Storage
- **UPLOAD_DIR**: Directory for file uploads (default ./uploads)
- **MAX_UPLOAD_SIZE_MB**: Maximum file size in MB (default 100)
- **ALLOWED_FILE_EXTENSIONS**: Comma-separated file types allowed

### Machine Learning Models
- **ML_MODELS_PATH**: Directory for model files
- **NLP_MODEL_NAME**: Hugging Face model (default bert-base-uncased)
- **NLP_MODEL_DEVICE**: CPU or GPU (cpu/cuda)
- **CV_MODEL_NAME**: Computer vision model
- **TS_MODEL_NAME**: Time series model

### Logging
- **LOG_LEVEL**: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **LOG_FORMAT**: Log format (json for structured logging)

---

## Development Setup

If doing development work:

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

3. **Run code quality checks**
   ```bash
   # Format code
   black .

   # Check linting
   flake8 backend/ frontend/ ml/

   # Type checking
   mypy backend/

   # Import sorting
   isort .
   ```

4. **Run tests**
   ```bash
   # Run all tests
   pytest

   # Run with coverage report
   pytest --cov=backend

   # Run specific test file
   pytest backend/tests/test_health.py -v
   ```

---

## Starting the Application

### Backend API Server
```bash
# Activate environment first
source venv/bin/activate

# Start FastAPI dev server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`  
API docs (Swagger): `http://localhost:8000/docs`

### Frontend (Streamlit)
```bash
# In a separate terminal, activate environment
source venv/bin/activate

# Start Streamlit app
streamlit run frontend/streamlit_app.py
```

Frontend will be available at: `http://localhost:8501`

### Using Makefile (Recommended)
```bash
# Start API server
make run-api

# Start frontend (in separate terminal)
make run-frontend

# Or start both (shows instructions)
make run-all
```

---

## Troubleshooting

### Import errors after activation
**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
- Ensure environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### PostgreSQL driver error
**Problem**: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution**:
```bash
pip install psycopg2-binary
```

If that fails, try:
```bash
pip install psycopg2-binary --no-cache-dir
```

### Torch/CUDA issues
**Problem**: Wrong CUDA version or CPU/GPU mismatch

**Solution for CPU-only**:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Solution for GPU (CUDA 11.8)**:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**Solution for GPU (CUDA 12.1)**:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Check your CUDA version:
```bash
nvidia-smi  # Shows CUDA version
```

### Transformers model download slow
**Problem**: First inference is very slow

**Reason**: Hugging Face transformers downloads the model (~440MB for BERT) on first use.

**Solution**: Pre-download model during setup:
```python
from transformers import AutoTokenizer, AutoModel

model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
```

### Permission denied on venv activation
**Problem**: `bash: ./venv/bin/activate: Permission denied`

**Solution** (macOS/Linux):
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

### .env file not found
**Problem**: `OSError: .env file not found`

**Solution**:
```bash
cp .env.example .env
# Then edit with your settings
```

---

## Deactivating Environment

```bash
deactivate
```

---

## Quick Reference

### Environment Setup
```bash
python3 -m venv venv                    # Create venv
source venv/bin/activate                # Activate venv (macOS/Linux)
venv\Scripts\activate                   # Activate venv (Windows)
pip install -r requirements.txt         # Install dependencies
pip list                                # List installed packages
pip freeze > requirements.txt           # Export installed packages
```

### Makefile Commands (Recommended)
```bash
make help                              # Show all available commands
make env-pip                           # Create pip venv
make env-setup                         # Set up .env file
make install-dev                       # Install dev dependencies
make test                              # Run tests
make lint                              # Run linters
make format                            # Format code
make run-api                           # Start API server
make run-frontend                      # Start frontend
make run-all                           # Show instructions to run both
make clean                             # Clean cache files
```

---

## Getting Help

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify Python version: `python --version` (should be 3.10+)
3. Check pip version: `pip --version` (should be latest)
4. Recreate environment from scratch if needed
5. Check README.md for additional documentation