"""Serve static files in production."""
from fastapi.staticfiles import StaticFiles
from pathlib import Path

def setup_static_files(app, frontend_dir: Path = None):
    """
    Setup static file serving for frontend.
    
    Args:
        app: FastAPI application instance
        frontend_dir: Path to frontend directory
    """
    if frontend_dir is None:
        frontend_dir = Path(__file__).parent.parent / "frontend"
    
    if frontend_dir.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
        # Also serve index.html at root
        @app.get("/")
        async def read_root():
            from fastapi.responses import FileResponse
            index_path = frontend_dir / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
            return {"message": "Frontend not found"}

