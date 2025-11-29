# Quick Start Guide

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start the backend server:**
```bash
python -m uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

3. **Open the frontend:**
   - Option 1: Open `frontend/index.html` directly in your browser
   - Option 2: Serve it with a simple HTTP server:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then navigate to `http://localhost:8080`

## Basic Workflow

1. **Upload Files:**
   - Upload your XCMS PeakTable CSV file
   - Upload one or more mzXML files
   - Upload a spectral library (MSP, MGF, JSON, or mzML)

2. **Configure Matching:**
   - Select algorithm (MS2Query recommended)
   - Adjust m/z and RT tolerances
   - Set minimum score threshold

3. **Run Matching:**
   - Click "Run Matching"
   - Wait for processing to complete

4. **View Results:**
   - Browse matched metabolites
   - View spectra
   - Export results

## API Documentation

When the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### MS2Query Not Working
If MS2Query matching fails, the system will automatically fall back to traditional cosine similarity matching.

### File Upload Issues
- Check file size limits (default: 500 MB)
- Verify file formats are supported
- Ensure files are not corrupted

### Port Already in Use
If port 8000 is in use, specify a different port:
```bash
python -m uvicorn backend.main:app --port 8001
```
Then update `frontend/js/api.js` to use the new port.

