"""Configuration settings for the application."""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
UPLOAD_DIR.mkdir(exist_ok=True)

# File upload settings
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_EXTENSIONS = {
    "xcms": [".csv"],
    "mzxml": [".mzxml", ".mzXML"],
    "library": [".msp", ".mgf", ".json", ".mzml", ".mzML"]
}

# MS2 extraction settings
DEFAULT_MZ_TOLERANCE = 0.01  # Da
DEFAULT_RT_TOLERANCE = 30.0  # seconds

# Matching settings
DEFAULT_MATCHING_ALGORITHM = "ms2query"
AVAILABLE_ALGORITHMS = ["ms2query", "dot_product", "cosine", "modified_cosine"]

