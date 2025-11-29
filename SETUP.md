# Setup Instructions

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

Check that all packages are installed correctly:

```bash
python -c "import fastapi, matchms, pandas, numpy; print('All packages installed successfully')"
```

### 3. (Optional) Install MS2Query Models

MS2Query will automatically download pre-trained models on first use. If you want to use your own library:

1. Prepare your spectral library in MSP, MGF, JSON, or mzML format
2. Train models using MS2Query's training functions
3. Place the model files in a directory accessible to the application

## Running the Application

### Option 1: Using the Convenience Script

```bash
python run_server.py
```

### Option 2: Using uvicorn Directly

```bash
python -m uvicorn backend.main:app --reload
```

### Option 3: Using Python Module

```bash
python -m backend
```

The server will start on `http://localhost:8000`

## Accessing the Application

### Frontend Options

1. **Direct File Access**: Open `frontend/index.html` in your browser
   - Note: API calls may be blocked by CORS. Use option 2 or 3 instead.

2. **Simple HTTP Server**:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then navigate to `http://localhost:8080`

3. **Serve via Backend** (Production):
   - Uncomment the static file serving in `backend/main.py`
   - Access at `http://localhost:8000`

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Configuration

### Backend Configuration

Edit `backend/config.py` to customize:
- File upload size limits
- Default matching parameters
- Allowed file extensions
- Upload directory location

### Frontend Configuration

Edit `frontend/js/api.js` to change:
- API base URL (default: `http://localhost:8000`)

## Troubleshooting

### Port Already in Use

If port 8000 is occupied:

```bash
python -m uvicorn backend.main:app --port 8001
```

Then update `frontend/js/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8001';
```

### MS2Query Not Working

If MS2Query matching fails:
1. Check that `ms2query` is installed: `pip install ms2query`
2. The application will automatically fall back to traditional matching
3. Check server logs for specific error messages

### Import Errors

If you see import errors:
1. Ensure you're running from the project root directory
2. Check that all dependencies are installed
3. Verify Python version is 3.9+

### File Upload Issues

- Check file size limits in `backend/config.py`
- Verify file formats are supported
- Ensure uploads directory exists and is writable

## Development Mode

For development with auto-reload:

```bash
python run_server.py
```

Or:

```bash
python -m uvicorn backend.main:app --reload --reload-dir backend
```

## Production Deployment

For production:

1. Set `reload=False` in uvicorn
2. Configure proper CORS origins
3. Use a production ASGI server (e.g., Gunicorn with uvicorn workers)
4. Set up proper file storage (not in uploads/ directory)
5. Configure environment variables for sensitive settings

Example with Gunicorn:

```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

