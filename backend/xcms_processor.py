"""XCMS processing module for peak detection and alignment."""
import subprocess
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from backend.config import UPLOAD_DIR, RESULTS_DIR
from backend.errors import XCMSProcessingError


def process_with_xcms(
    mzxml_files: List[Path],
    output_dir: Path,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process mzXML files using XCMS to generate peak table.
    
    This function can use either:
    1. R XCMS package via rpy2 or subprocess
    2. pyOpenMS (OpenMS Python bindings)
    3. External R script
    
    Args:
        mzxml_files: List of paths to mzXML files
        output_dir: Directory to save results
        params: XCMS processing parameters
        
    Returns:
        Dictionary with processing results and output file paths
    """
    if params is None:
        params = get_default_xcms_params()
    
    # Check available XCMS implementation
    if check_r_xcms_available():
        return process_with_r_xcms(mzxml_files, output_dir, params)
    elif check_pyopenms_available():
        return process_with_pyopenms(mzxml_files, output_dir, params)
    else:
        raise XCMSProcessingError(
            "No XCMS implementation available. Please install R with XCMS package or pyOpenMS."
        )


def get_default_xcms_params() -> Dict[str, Any]:
    """Get default XCMS processing parameters."""
    return {
        "ppm": 10,
        "peakwidth": [5, 30],
        "snthresh": 6,
        "mzdiff": 0.01,
        "quant_method": "into",
        "minfrac": 0.5,
        "minsamp": 0,
        "bw": 5,
        "mzwid": 0.006,
        "peak_detection_method": "centWave",
        "peak_grouping_method": "density",
        "rt_correction_method": "obiwarp"
    }


def check_r_xcms_available() -> bool:
    """Check if R with XCMS package is available."""
    try:
        result = subprocess.run(
            ["Rscript", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Check if XCMS is installed
            check_xcms = subprocess.run(
                ["Rscript", "-e", "library(xcms)"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return check_xcms.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False


def check_pyopenms_available() -> bool:
    """Check if pyOpenMS is available."""
    try:
        import pyopenms
        return True
    except ImportError:
        return False


def process_with_r_xcms(
    mzxml_files: List[Path],
    output_dir: Path,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process files using R XCMS package.
    
    Args:
        mzxml_files: List of mzXML file paths
        output_dir: Output directory
        params: XCMS parameters
        
    Returns:
        Dictionary with results
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create R script for XCMS processing
    r_script = generate_xcms_r_script(mzxml_files, output_dir, params)
    
    # Save R script to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
        r_script_path = Path(f.name)
        f.write(r_script)
    
    try:
        # Run R script
        result = subprocess.run(
            ["Rscript", str(r_script_path)],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode != 0:
            raise XCMSProcessingError(f"XCMS processing failed: {result.stderr}")
        
        # Check for output files
        peak_table_path = output_dir / "PeakTable_verbose.csv"
        sample_info_path = output_dir / "sample.info.csv"
        
        if not peak_table_path.exists():
            raise XCMSProcessingError("Peak table file not generated")
        
        return {
            "success": True,
            "peak_table": str(peak_table_path),
            "sample_info": str(sample_info_path) if sample_info_path.exists() else None,
            "output_dir": str(output_dir),
            "message": "XCMS processing completed successfully"
        }
    finally:
        # Clean up temporary R script
        if r_script_path.exists():
            r_script_path.unlink()


def generate_xcms_r_script(
    mzxml_files: List[Path],
    output_dir: Path,
    params: Dict[str, Any]
) -> str:
    """Generate R script for XCMS processing."""
    file_paths = [str(f.absolute()) for f in mzxml_files]
    file_paths_str = "c(" + ", ".join([f'"{p}"' for p in file_paths]) + ")"
    
    script = f"""
# XCMS Processing Script
library(xcms)
library(CAMERA)

# File paths
mzxml_files <- {file_paths_str}
output_dir <- "{output_dir.absolute()}"

# Create output directory
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# Load files
xset <- xcmsSet(
    files = mzxml_files,
    method = "{params.get('peak_detection_method', 'centWave')}",
    ppm = {params.get('ppm', 10)},
    peakwidth = c({params.get('peakwidth', [5, 30])[0]}, {params.get('peakwidth', [5, 30])[1]}),
    snthresh = {params.get('snthresh', 6)},
    mzdiff = {params.get('mzdiff', 0.01)},
    prefilter = c({params.get('prefilter', [3, 100])[0]}, {params.get('prefilter', [3, 100])[1]})
)

# Group peaks
xset <- group(
    xset,
    method = "{params.get('peak_grouping_method', 'density')}",
    bw = {params.get('bw', 5)},
    mzwid = {params.get('mzwid', 0.006)},
    minfrac = {params.get('minfrac', 0.5)},
    minsamp = {params.get('minsamp', 0)}
)

# Retention time correction
xset <- retcor(
    xset,
    method = "{params.get('rt_correction_method', 'obiwarp')}"
)

# Regroup after RT correction
xset <- group(
    xset,
    method = "{params.get('peak_grouping_method', 'density')}",
    bw = {params.get('bw', 5)},
    mzwid = {params.get('mzwid', 0.006)},
    minfrac = {params.get('minfrac', 0.5)},
    minsamp = {params.get('minsamp', 0)}
)

# Fill peaks
xset <- fillPeaks(xset)

# Generate peak table
peak_table <- peakTable(xset)

# Save peak table
write.csv(peak_table, file = file.path(output_dir, "PeakTable_verbose.csv"), row.names = FALSE)

# Generate sample info
sample_names <- basename(mzxml_files)
sample_info <- data.frame(
    sample.name = sample_names,
    group = rep(".", length(sample_names)),
    stringsAsFactors = FALSE
)
write.csv(sample_info, file = file.path(output_dir, "sample.info.csv"), row.names = FALSE)

cat("XCMS processing completed successfully\\n")
"""
    return script


def process_with_pyopenms(
    mzxml_files: List[Path],
    output_dir: Path,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process files using pyOpenMS (OpenMS Python bindings).
    
    Note: pyOpenMS has different API than R XCMS, so this is a simplified implementation.
    For full XCMS compatibility, use R XCMS.
    
    Args:
        mzxml_files: List of mzXML file paths
        output_dir: Output directory
        params: Processing parameters
        
    Returns:
        Dictionary with results
    """
    try:
        import pyopenms as oms
    except ImportError:
        raise XCMSProcessingError("pyOpenMS not available")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # This is a placeholder - pyOpenMS has different workflow
    # For now, we'll use a simplified approach
    # In production, you'd want to implement full OpenMS workflow
    
    # Load and process files
    all_peaks = []
    sample_names = []
    
    for mzxml_file in mzxml_files:
        exp = oms.MSExperiment()
        oms.MzXMLFile().load(str(mzxml_file), exp)
        
        # Simple peak picking (simplified - not full XCMS equivalent)
        # In practice, you'd use OpenMS FeatureFinder or similar
        
        sample_names.append(mzxml_file.stem)
    
    # Generate peak table (simplified)
    # This would need full OpenMS workflow implementation
    
    raise XCMSProcessingError(
        "Full pyOpenMS XCMS workflow not yet implemented. "
        "Please use R XCMS or provide pre-processed XCMS results."
    )


def load_xcms_params_from_yaml(yaml_path: Path) -> Dict[str, Any]:
    """Load XCMS parameters from YAML file."""
    try:
        import yaml
        with open(yaml_path, 'r') as f:
            params = yaml.safe_load(f)
        return params
    except Exception as e:
        print(f"Warning: Could not load YAML params: {e}")
        return get_default_xcms_params()


def validate_xcms_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize XCMS parameters."""
    validated = get_default_xcms_params()
    validated.update(params)
    
    # Ensure peakwidth is a list
    if isinstance(validated.get("peakwidth"), (int, float)):
        validated["peakwidth"] = [validated["peakwidth"], validated["peakwidth"] * 2]
    
    # Ensure prefilter is a list
    if isinstance(validated.get("prefilter"), (int, float)):
        validated["prefilter"] = [validated["prefilter"], validated["prefilter"] * 10]
    
    return validated

