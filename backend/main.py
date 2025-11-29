"""FastAPI application for XCMS metabolite MS2 matching."""
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path
import json
import asyncio
from typing import List, Optional, Dict, Any

from backend.config import UPLOAD_DIR, RESULTS_DIR
from backend.models import (
    MatchingConfig, MS2ExtractionConfig, ProcessingStatus,
    XCMSProcessingConfig, XCMSProcessingResult
)
from backend.data_loader import load_xcms_data, get_peak_info
from backend.ms2_extractor import extract_ms2_spectra
from backend.library_parser import parse_library_file
from backend.ms2query_matcher import match_with_ms2query, is_ms2query_available
from backend.spectral_matcher import match_with_traditional
from backend.results_processor import process_matching_results
from backend.xcms_processor import (
    process_with_xcms, get_default_xcms_params,
    check_r_xcms_available, check_pyopenms_available,
    load_xcms_params_from_yaml, validate_xcms_params
)
from backend.errors import MS2ExtractionError, LibraryParseError, MatchingError, XCMSProcessingError

app = FastAPI(title="XCMS Metabolite MS2 Matching Tool", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []


async def broadcast_progress(job_id: str, status: str, progress: float, message: str = None):
    """Broadcast progress update to all connected clients."""
    data = {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "message": message
    }
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except:
            disconnected.append(connection)
    for conn in disconnected:
        active_connections.remove(conn)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "XCMS Metabolite MS2 Matching Tool API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/upload/xcms")
async def upload_xcms_results(file: UploadFile = File(...)):
    """Upload XCMS results CSV file."""
    try:
        file_path = UPLOAD_DIR / f"xcms_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "filename": file.filename,
            "path": str(file_path),
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/mzxml")
async def upload_mzxml(file: UploadFile = File(...)):
    """Upload mzXML file."""
    try:
        file_path = UPLOAD_DIR / f"mzxml_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "filename": file.filename,
            "path": str(file_path),
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/library")
async def upload_library(file: UploadFile = File(...)):
    """Upload spectral library file."""
    try:
        file_path = UPLOAD_DIR / f"library_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Try to parse the library to validate
        try:
            library_data = parse_library_file(file_path)
            return {
                "filename": file.filename,
                "path": str(file_path),
                "size": len(content),
                "spectra_count": len(library_data) if isinstance(library_data, list) else 1,
                "valid": True
            }
        except Exception as parse_error:
            return {
                "filename": file.filename,
                "path": str(file_path),
                "size": len(content),
                "valid": False,
                "error": str(parse_error)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/xcms/peaks")
async def get_xcms_peaks(xcms_file: str):
    """Get XCMS peak data."""
    try:
        file_path = UPLOAD_DIR / xcms_file
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="XCMS file not found")
        
        data = load_xcms_data(file_path)
        return {"peaks": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract/ms2")
async def extract_ms2(
    mzxml_file: str,
    xcms_file: str,
    config: MS2ExtractionConfig
):
    """Extract MS2 spectra from mzXML file."""
    try:
        mzxml_path = UPLOAD_DIR / mzxml_file
        xcms_path = UPLOAD_DIR / xcms_file
        
        if not mzxml_path.exists():
            raise HTTPException(status_code=404, detail="mzXML file not found")
        if not xcms_path.exists():
            raise HTTPException(status_code=404, detail="XCMS file not found")
        
        spectra = extract_ms2_spectra(
            mzxml_path,
            xcms_path,
            mz_tolerance=config.mz_tolerance,
            rt_tolerance=config.rt_tolerance,
            min_intensity=config.min_intensity
        )
        
        return {"spectra_count": len(spectra), "spectra": spectra}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/match/spectra")
async def match_spectra(request_data: Dict[str, Any] = Body(...)):
    """Perform complete spectral matching workflow."""
    try:
        mzxml_file = request_data.get("mzxml_file")
        xcms_file = request_data.get("xcms_file")
        library_file = request_data.get("library_file")
        algorithm = request_data.get("algorithm", "ms2query")
        
        config_data = request_data.get("config", {})
        if isinstance(config_data, dict) and config_data:
            config = MatchingConfig(**config_data)
        else:
            config = MatchingConfig()
        
        mzxml_path = UPLOAD_DIR / mzxml_file
        xcms_path = UPLOAD_DIR / xcms_file
        library_path = UPLOAD_DIR / library_file
        
        if not mzxml_path.exists():
            raise HTTPException(status_code=404, detail="mzXML file not found")
        if not xcms_path.exists():
            raise HTTPException(status_code=404, detail="XCMS file not found")
        if not library_path.exists():
            raise HTTPException(status_code=404, detail="Library file not found")
        
        # Step 1: Extract MS2 spectra
        extraction_config = MS2ExtractionConfig(
            mz_tolerance=config.mz_tolerance,
            rt_tolerance=config.rt_tolerance
        )
        ms2_spectra_data = extract_ms2_spectra(
            mzxml_path,
            xcms_path,
            mz_tolerance=extraction_config.mz_tolerance,
            rt_tolerance=extraction_config.rt_tolerance,
            min_intensity=extraction_config.min_intensity
        )
        
        # Convert to matchms Spectrum objects
        from backend.ms2_extractor import convert_to_matchms_spectrum
        query_spectra = [convert_to_matchms_spectrum(s) for s in ms2_spectra_data]
        
        # Step 2: Load library
        library_spectra = parse_library_file(library_path)
        
        # Step 3: Perform matching
        if algorithm == "ms2query":
            try:
                from backend.ms2query_matcher import is_ms2query_available
                if is_ms2query_available():
                    matching_results = match_with_ms2query(
                        query_spectra,
                        library_path=library_path.parent,
                        analog_search=True,
                        top_n=config.top_n
                    )
                else:
                    raise ImportError("MS2Query not available")
            except (ImportError, ValueError, Exception) as e:
                # Fallback to traditional if MS2Query fails
                print(f"MS2Query failed ({str(e)}), using traditional matching")
                matching_results = match_with_traditional(
                    query_spectra,
                    library_spectra,
                    algorithm="cosine",
                    mz_tolerance=config.mz_tolerance,
                    min_score=config.min_score,
                    top_n=config.top_n
                )
                algorithm = "cosine"  # Update algorithm name for results
        else:
            matching_results = match_with_traditional(
                query_spectra,
                library_spectra,
                algorithm=algorithm,
                mz_tolerance=config.mz_tolerance,
                min_score=config.min_score,
                top_n=config.top_n
            )
        
        # Step 4: Process results
        xcms_peaks = load_xcms_data(xcms_path)
        processed_results = process_matching_results(
            xcms_peaks,
            matching_results,
            algorithm=algorithm
        )
        
        return {
            "extraction": {
                "spectra_count": len(ms2_spectra_data),
                "spectra": ms2_spectra_data
            },
            "matching": {
                "algorithm": algorithm,
                "matches": matching_results,
                "processed_results": processed_results
            },
            "config": config.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    """WebSocket endpoint for progress updates."""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or process client messages
            await websocket.send_json({"received": data})
    except WebSocketDisconnect:
        active_connections.remove(websocket)


# Serve static files in production (uncomment if needed)
# from backend.static_files import setup_static_files
# setup_static_files(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

