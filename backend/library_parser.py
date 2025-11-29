"""Parse spectral library files in multiple formats."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from matchms import importing
from matchms import Spectrum
import json


def parse_library_file(file_path: Path) -> List[Spectrum]:
    """
    Parse spectral library file in various formats.
    
    Supported formats: MSP, MGF, JSON, mzML
    
    Args:
        file_path: Path to library file
        
    Returns:
        List of matchms Spectrum objects
    """
    file_extension = file_path.suffix.lower()
    
    if file_extension == ".msp":
        return parse_msp_file(file_path)
    elif file_extension == ".mgf":
        return parse_mgf_file(file_path)
    elif file_extension == ".json":
        return parse_json_file(file_path)
    elif file_extension in [".mzml", ".mzxml"]:
        return parse_mzml_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def parse_msp_file(file_path: Path) -> List[Spectrum]:
    """Parse MSP (NIST) format library file."""
    try:
        spectra = list(importing.load_from_msp(str(file_path)))
        return spectra
    except Exception as e:
        raise ValueError(f"Error parsing MSP file: {str(e)}")


def parse_mgf_file(file_path: Path) -> List[Spectrum]:
    """Parse MGF (Mascot Generic Format) library file."""
    try:
        spectra = list(importing.load_from_mgf(str(file_path)))
        return spectra
    except Exception as e:
        raise ValueError(f"Error parsing MGF file: {str(e)}")


def parse_json_file(file_path: Path) -> List[Spectrum]:
    """Parse JSON format library file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        spectra = []
        if isinstance(data, list):
            for item in data:
                spectrum = parse_json_spectrum(item)
                if spectrum:
                    spectra.append(spectrum)
        elif isinstance(data, dict):
            spectrum = parse_json_spectrum(data)
            if spectrum:
                spectra.append(spectrum)
        
        return spectra
    except Exception as e:
        raise ValueError(f"Error parsing JSON file: {str(e)}")


def parse_json_spectrum(data: Dict[str, Any]) -> Optional[Spectrum]:
    """Parse a single spectrum from JSON data."""
    try:
        mz = data.get("mz", [])
        intensities = data.get("intensities", [])
        
        if not mz or not intensities:
            return None
        
        metadata = data.get("metadata", {})
        
        spectrum = Spectrum(
            mz=mz,
            intensities=intensities,
            metadata=metadata
        )
        
        return spectrum
    except Exception as e:
        print(f"Error parsing JSON spectrum: {str(e)}")
        return None


def parse_mzml_file(file_path: Path) -> List[Spectrum]:
    """Parse mzML format library file."""
    try:
        spectra = list(importing.load_from_mzml(str(file_path)))
        return spectra
    except Exception as e:
        raise ValueError(f"Error parsing mzML file: {str(e)}")


def get_library_info(spectra: List[Spectrum]) -> Dict[str, Any]:
    """
    Get summary information about a library.
    
    Args:
        spectra: List of library spectra
        
    Returns:
        Dictionary with library statistics
    """
    if len(spectra) == 0:
        return {
            "count": 0,
            "compounds": [],
            "precursor_mz_range": None,
            "formats": []
        }
    
    compounds = []
    precursor_mzs = []
    
    for spectrum in spectra:
        # Get compound name
        compound_name = spectrum.get("compound_name") or \
                       spectrum.get("name") or \
                       spectrum.get("title", "Unknown")
        compounds.append(compound_name)
        
        # Get precursor m/z
        precursor_mz = spectrum.get("precursor_mz")
        if precursor_mz:
            precursor_mzs.append(float(precursor_mz))
    
    info = {
        "count": len(spectra),
        "compounds": list(set(compounds)),
        "precursor_mz_range": {
            "min": min(precursor_mzs) if precursor_mzs else None,
            "max": max(precursor_mzs) if precursor_mzs else None
        },
        "formats": ["matchms"]
    }
    
    return info

