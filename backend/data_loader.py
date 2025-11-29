"""Load and parse XCMS results."""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_xcms_data(csv_path: Path) -> List[Dict[str, Any]]:
    """
    Load XCMS PeakTable CSV file.
    
    Args:
        csv_path: Path to the XCMS PeakTable CSV file
        
    Returns:
        List of dictionaries containing peak information
    """
    try:
        df = pd.read_csv(csv_path)
        
        # Convert to list of dictionaries
        peaks = []
        for _, row in df.iterrows():
            peak_data = {
                "name": str(row.get("name", "")),
                "mz": float(row.get("mz", 0.0)),
                "mzmin": float(row.get("mzmin", 0.0)),
                "mzmax": float(row.get("mzmax", 0.0)),
                "rt": float(row.get("rt", 0.0)),
                "rtmin": float(row.get("rtmin", 0.0)),
                "rtmax": float(row.get("rtmax", 0.0)),
                "npeaks": int(row.get("npeaks", 0)),
                "intensities": {}
            }
            
            # Extract intensity values for each sample
            # Skip metadata columns
            skip_cols = {"name", "mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax", "npeaks", "."}
            for col in df.columns:
                if col not in skip_cols:
                    value = row.get(col)
                    if pd.notna(value):
                        try:
                            peak_data["intensities"][col] = float(value)
                        except (ValueError, TypeError):
                            pass
            
            peaks.append(peak_data)
        
        return peaks
    except Exception as e:
        raise ValueError(f"Error loading XCMS data: {str(e)}")


def load_sample_info(csv_path: Path) -> Dict[str, str]:
    """
    Load sample information CSV file.
    
    Args:
        csv_path: Path to the sample.info.csv file
        
    Returns:
        Dictionary mapping sample names to groups
    """
    try:
        df = pd.read_csv(csv_path)
        sample_info = {}
        for _, row in df.iterrows():
            sample_name = str(row.get("sample.name", ""))
            group = str(row.get("group", ""))
            sample_info[sample_name] = group
        return sample_info
    except Exception as e:
        raise ValueError(f"Error loading sample info: {str(e)}")


def get_peak_info(peaks: List[Dict[str, Any]], peak_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information for a specific peak by name.
    
    Args:
        peaks: List of peak dictionaries
        peak_name: Name of the peak to retrieve
        
    Returns:
        Peak dictionary or None if not found
    """
    for peak in peaks:
        if peak.get("name") == peak_name:
            return peak
    return None


def filter_peaks(
    peaks: List[Dict[str, Any]],
    mz_min: Optional[float] = None,
    mz_max: Optional[float] = None,
    rt_min: Optional[float] = None,
    rt_max: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Filter peaks by m/z and retention time ranges.
    
    Args:
        peaks: List of peak dictionaries
        mz_min: Minimum m/z value
        mz_max: Maximum m/z value
        rt_min: Minimum retention time
        rt_max: Maximum retention time
        
    Returns:
        Filtered list of peaks
    """
    filtered = peaks
    
    if mz_min is not None:
        filtered = [p for p in filtered if p.get("mz", 0) >= mz_min]
    if mz_max is not None:
        filtered = [p for p in filtered if p.get("mz", 0) <= mz_max]
    if rt_min is not None:
        filtered = [p for p in filtered if p.get("rt", 0) >= rt_min]
    if rt_max is not None:
        filtered = [p for p in filtered if p.get("rt", 0) <= rt_max]
    
    return filtered

