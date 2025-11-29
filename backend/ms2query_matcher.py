"""MS2Query integration for ML-assisted spectral matching."""
from typing import List, Dict, Any, Optional
from pathlib import Path
from matchms import Spectrum
import numpy as np

try:
    from ms2query.ms2library import MS2Library
    from ms2query.run_ms2query import run_complete_folder
    MS2QUERY_AVAILABLE = True
except ImportError:
    MS2QUERY_AVAILABLE = False
    print("Warning: MS2Query not available. Install with: pip install ms2query")


def match_with_ms2query(
    query_spectra: List[Spectrum],
    library_path: Optional[Path] = None,
    ms2library: Optional[Any] = None,
    analog_search: bool = True,
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Match query spectra against library using MS2Query.
    
    Args:
        query_spectra: List of matchms Spectrum objects to match
        library_path: Path to MS2Query library directory (optional if ms2library provided)
        ms2library: Pre-initialized MS2Library object (optional)
        analog_search: Whether to perform analog search (True) or exact match only (False)
        top_n: Number of top matches to return per query
        
    Returns:
        List of matching results dictionaries
    """
    if not MS2QUERY_AVAILABLE:
        raise ImportError("MS2Query is not installed. Install with: pip install ms2query")
    
    results = []
    
    # Initialize library if not provided
    if ms2library is None:
        if library_path is None:
            raise ValueError("Either library_path or ms2library must be provided")
        try:
            # Try to create library from directory
            # MS2Query expects a directory with model files
            from ms2query.ms2library import create_library_object_from_one_dir
            try:
                ms2library = create_library_object_from_one_dir(str(library_path.parent))
            except:
                # Fallback: try to load from sqlite file if it exists
                sqlite_file = library_path.parent / "library.sqlite"
                if sqlite_file.exists():
                    ms2library = MS2Library(sqlite_file_name=str(sqlite_file))
                else:
                    raise ValueError("MS2Query library files not found. Please ensure library directory contains required model files.")
        except Exception as e:
            raise ValueError(f"Error loading MS2Query library: {str(e)}")
    
    # Match each query spectrum
    for i, query_spectrum in enumerate(query_spectra):
        try:
            # Run MS2Query matching
            # Note: MS2Query API may vary by version - this is a common pattern
            try:
                # Try the match_spectrum method
                matches = ms2library.match_spectrum(
                    query_spectrum,
                    analog_search=analog_search,
                    number_of_results=top_n
                )
            except AttributeError:
                # Alternative API: use run_ms2query functions
                from ms2query.run_ms2query import run_ms2query
                matches = run_ms2query(
                    query_spectrum,
                    ms2library,
                    analog_search=analog_search,
                    number_of_results=top_n
                )
            
            match_results = []
            for match in matches:
                match_dict = {
                    "library_id": match.get("library_id", ""),
                    "compound_name": match.get("compound_name", ""),
                    "score": float(match.get("ms2query_score", 0.0)),
                    "algorithm": "ms2query",
                    "matched_peaks": match.get("matched_peaks", 0),
                    "total_peaks": len(query_spectrum.peaks.mz),
                    "metadata": {
                        "precursor_mz": match.get("precursor_mz"),
                        "retention_time": match.get("retention_time"),
                        "smiles": match.get("smiles"),
                        "inchi": match.get("inchi"),
                        "inchikey": match.get("inchikey"),
                        "analog": match.get("analog", False)
                    }
                }
                match_results.append(match_dict)
            
            results.append({
                "query_index": i,
                "query_spectrum": {
                    "precursor_mz": query_spectrum.get("precursor_mz"),
                    "retention_time": query_spectrum.get("retention_time")
                },
                "matches": match_results,
                "best_match": match_results[0] if match_results else None
            })
            
        except Exception as e:
            print(f"Error matching spectrum {i}: {str(e)}")
            results.append({
                "query_index": i,
                "error": str(e),
                "matches": []
            })
    
    return results


def create_ms2query_library(
    library_spectra: List[Spectrum],
    output_path: Path,
    ion_mode: str = "positive"
) -> Path:
    """
    Create an MS2Query library from matchms spectra.
    
    Args:
        library_spectra: List of matchms Spectrum objects
        output_path: Directory to save the library
        ion_mode: Ionization mode ("positive" or "negative")
        
    Returns:
        Path to created library directory
    """
    if not MS2QUERY_AVAILABLE:
        raise ImportError("MS2Query is not installed")
    
    try:
        from ms2query.create_new_library.train_models import clean_and_train_models
        
        # Save spectra to temporary file first
        temp_file = output_path / "library_spectra.mgf"
        from matchms import exporting
        exporting.save_as_mgf(list(library_spectra), str(temp_file))
        
        # Train models
        clean_and_train_models(
            spectrum_file=str(temp_file),
            ion_mode=ion_mode,
            output_folder=str(output_path)
        )
        
        return output_path
    except Exception as e:
        raise ValueError(f"Error creating MS2Query library: {str(e)}")


def is_ms2query_available() -> bool:
    """Check if MS2Query is available."""
    return MS2QUERY_AVAILABLE

