"""Extract MS2 spectra from mzXML files and match to XCMS features."""
import pymzml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from matchms import Spectrum
import numpy as np
from backend.data_loader import load_xcms_data


def extract_ms2_spectra(
    mzxml_path: Path,
    xcms_csv_path: Path,
    mz_tolerance: float = 0.01,
    rt_tolerance: float = 30.0,
    min_intensity: float = 100.0
) -> List[Dict[str, Any]]:
    """
    Extract MS2 spectra from mzXML file and match to XCMS features.
    
    Args:
        mzxml_path: Path to mzXML file
        xcms_csv_path: Path to XCMS PeakTable CSV
        mz_tolerance: m/z tolerance for matching (Da)
        rt_tolerance: Retention time tolerance (seconds)
        min_intensity: Minimum intensity threshold
        
    Returns:
        List of dictionaries containing matched MS2 spectra
    """
    # Load XCMS peaks
    xcms_peaks = load_xcms_data(xcms_csv_path)
    
    # Extract MS2 spectra from mzXML
    ms2_spectra = []
    run = pymzml.run.Reader(str(mzxml_path))
    
    for spectrum in run:
        if spectrum.ms_level == 2:
            # Get precursor information
            precursor_mz = None
            precursor_rt = None
            
            # Try to get precursor m/z
            if hasattr(spectrum, 'precursors'):
                if len(spectrum.precursors) > 0:
                    precursor_mz = spectrum.precursors[0].get('mz', None)
            
            # Get retention time
            if hasattr(spectrum, 'scan_time'):
                precursor_rt = spectrum.scan_time[0] * 60  # Convert to seconds
            
            if precursor_mz is None or precursor_rt is None:
                continue
            
            # Extract peaks
            peaks = []
            if hasattr(spectrum, 'peaks'):
                for mz, intensity in spectrum.peaks:
                    if intensity >= min_intensity:
                        peaks.append((float(mz), float(intensity)))
            
            if len(peaks) == 0:
                continue
            
            # Match to XCMS features
            matched_peak = find_matching_xcms_peak(
                xcms_peaks,
                precursor_mz,
                precursor_rt,
                mz_tolerance,
                rt_tolerance
            )
            
            if matched_peak:
                # Convert to matchms Spectrum object
                mz_array = np.array([p[0] for p in peaks])
                intensities_array = np.array([p[1] for p in peaks])
                
                spectrum_dict = {
                    "feature_name": matched_peak["name"],
                    "precursor_mz": precursor_mz,
                    "rt": precursor_rt,
                    "mz": mz_array.tolist(),
                    "intensities": intensities_array.tolist(),
                    "n_peaks": len(peaks),
                    "matched_xcms_peak": matched_peak["name"]
                }
                ms2_spectra.append(spectrum_dict)
    
    return ms2_spectra


def find_matching_xcms_peak(
    xcms_peaks: List[Dict[str, Any]],
    mz: float,
    rt: float,
    mz_tolerance: float,
    rt_tolerance: float
) -> Optional[Dict[str, Any]]:
    """
    Find XCMS peak that matches given m/z and RT.
    
    Args:
        xcms_peaks: List of XCMS peak dictionaries
        mz: Precursor m/z
        rt: Retention time in seconds
        mz_tolerance: m/z tolerance (Da)
        rt_tolerance: RT tolerance (seconds)
        
    Returns:
        Matching XCMS peak dictionary or None
    """
    best_match = None
    best_score = float('inf')
    
    for peak in xcms_peaks:
        peak_mz = peak.get("mz", 0)
        peak_rt = peak.get("rt", 0)
        
        mz_diff = abs(peak_mz - mz)
        rt_diff = abs(peak_rt - rt)
        
        if mz_diff <= mz_tolerance and rt_diff <= rt_tolerance:
            # Score based on combined distance (weighted)
            score = (mz_diff / mz_tolerance) + (rt_diff / rt_tolerance)
            if score < best_score:
                best_score = score
                best_match = peak
    
    return best_match


def convert_to_matchms_spectrum(spectrum_dict: Dict[str, Any]) -> Spectrum:
    """
    Convert spectrum dictionary to matchms Spectrum object.
    
    Args:
        spectrum_dict: Dictionary containing spectrum data
        
    Returns:
        matchms Spectrum object
    """
    mz = np.array(spectrum_dict["mz"])
    intensities = np.array(spectrum_dict["intensities"])
    
    metadata = {
        "precursor_mz": spectrum_dict["precursor_mz"],
        "retention_time": spectrum_dict["rt"],
        "feature_name": spectrum_dict.get("feature_name", ""),
        "charge": 1  # Default, can be updated if available
    }
    
    spectrum = Spectrum(
        mz=mz,
        intensities=intensities,
        metadata=metadata
    )
    
    return spectrum

